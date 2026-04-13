from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal, InvalidOperation
from .models import Withdrawal, WithdrawalMethod, Transaction
from .easypaisa_gateway import EasyPaisaGateway, process_easypaisa_withdrawal


def payment_dashboard(request):
    """Payment dashboard - accessible without login"""
    context = {
        'balance': 0,
        'total_earned': 0,
        'total_withdrawn': 0,
        'withdrawal_methods': WithdrawalMethod.objects.filter(is_active=True),
        'recent_withdrawals': [],
        'recent_transactions': [],
        'pending_withdrawals': 0,
        'is_logged_in': request.user.is_authenticated,
    }
    
    if request.user.is_authenticated:
        user = request.user
        context.update({
            'balance': user.balance,
            'total_earned': user.total_earned,
            'total_withdrawn': user.total_withdrawn,
            'recent_withdrawals': Withdrawal.objects.filter(user=user)[:10],
            'recent_transactions': Transaction.objects.filter(user=user)[:15],
            'pending_withdrawals': Withdrawal.objects.filter(
                user=user, 
                status='pending'
            ).count(),
        })
    
    return render(request, 'payments/payment_dashboard.html', context)


def withdraw(request):
    """Withdrawal page - redirects to login if not authenticated"""
    if not request.user.is_authenticated:
        from django.contrib.auth.views import redirect_to_login
        return redirect_to_login(request.get_full_path(), login_url='login')
    
    user = request.user
    withdrawal_methods = WithdrawalMethod.objects.filter(is_active=True)

    context = {
        'balance': user.balance,
        'withdrawal_methods': withdrawal_methods,
    }
    return render(request, 'payments/withdraw.html', context)


@login_required
def submit_withdrawal(request):
    """Submit withdrawal request"""
    if request.method != 'POST':
        return redirect('withdraw')
    
    user = request.user
    method_id = request.POST.get('method')
    amount_str = request.POST.get('amount', '0')
    account_number = request.POST.get('account_number')
    account_name = request.POST.get('account_name')

    # Convert amount to Decimal
    try:
        amount = Decimal(amount_str)
    except (InvalidOperation, ValueError):
        messages.error(request, 'Invalid amount')
        return redirect('withdraw')

    # Validation
    try:
        method = WithdrawalMethod.objects.get(id=method_id, is_active=True)
    except WithdrawalMethod.DoesNotExist:
        messages.error(request, 'Invalid withdrawal method')
        return redirect('withdraw')

    if amount < method.min_amount:
        messages.error(request, f'Minimum withdrawal is ${method.min_amount}')
        return redirect('withdraw')

    if amount > method.max_amount:
        messages.error(request, f'Maximum withdrawal is ${method.max_amount}')
        return redirect('withdraw')

    if amount > user.balance:
        messages.error(request, 'Insufficient balance')
        return redirect('withdraw')

    if not account_number or not account_name:
        messages.error(request, 'Please provide account details')
        return redirect('withdraw')

    # Calculate fee
    fee = amount * method.fee_percentage / Decimal('100')
    net_amount = amount - fee
    
    # Process withdrawal
    with transaction.atomic():
        # Create withdrawal record
        payment_details = {
            'method_name': method.name,
            'processing_time': method.processing_time,
        }
        
        withdrawal = Withdrawal.objects.create(
            user=user,
            method=method,
            amount=amount,
            fee=fee,
            net_amount=net_amount,
            account_number=account_number,
            account_name=account_name,
            payment_details=payment_details,
            status='pending'
        )
        
        # Deduct from user balance
        user.balance -= amount
        user.total_withdrawn += amount
        user.save()
        
        # Create transaction record
        Transaction.objects.create(
            user=user,
            type='withdrawal',
            amount=-amount,
            balance_after=user.balance,
            description=f'Withdrawal via {method.name}',
            reference_id=str(withdrawal.id)
        )
    
    messages.success(request, f'Withdrawal request of ${amount} submitted successfully!')
    return redirect('payment_dashboard')


def transaction_history(request):
    """Transaction history - redirects to login if not authenticated"""
    if not request.user.is_authenticated:
        from django.contrib.auth.views import redirect_to_login
        return redirect_to_login(request.get_full_path(), login_url='login')
    
    user = request.user
    transactions = Transaction.objects.filter(user=user)[:50]

    context = {
        'transactions': transactions,
    }
    return render(request, 'payments/transaction_history.html', context)


@csrf_exempt
def easypaisa_callback(request):
    """
    EasyPaisa payment callback endpoint.
    EasyPaisa will POST here after payment is processed.
    """
    if request.method == 'POST':
        order_ref = request.POST.get('orderRefNum')
        payment_status = request.POST.get('paymentStatus', '').lower()
        transaction_id = request.POST.get('txnid', '')
        
        # Find withdrawal by order reference
        if order_ref and order_ref.startswith('EP_'):
            try:
                withdrawal_id = order_ref.split('_')[1]
                withdrawal = Withdrawal.objects.get(id=withdrawal_id)
                
                with transaction.atomic():
                    if payment_status in ('success', 'completed'):
                        withdrawal.status = 'completed'
                        withdrawal.transaction_id = transaction_id or withdrawal.transaction_id
                        withdrawal.save()
                    elif payment_status in ('failed', 'error'):
                        withdrawal.status = 'failed'
                        withdrawal.save()
                        # Refund user
                        withdrawal.user.balance += withdrawal.amount
                        withdrawal.user.save()
                
                return JsonResponse({'status': 'ok'})
            except (Withdrawal.DoesNotExist, ValueError, IndexError):
                pass
    
    return JsonResponse({'status': 'error'}, status=400)


@login_required
def check_easypaisa_status(request, withdrawal_id):
    """
    Check EasyPaisa transaction status for a withdrawal.
    Admin can use this to verify payment status.
    """
    if not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    withdrawal = get_object_or_404(Withdrawal, id=withdrawal_id)
    
    if not withdrawal.transaction_id:
        return JsonResponse({'error': 'No transaction ID'}, status=400)
    
    gateway = EasyPaisaGateway()
    result = gateway.check_transaction_status(withdrawal.transaction_id)
    
    return JsonResponse({
        'withdrawal_id': withdrawal.id,
        'transaction_id': withdrawal.transaction_id,
        'current_status': withdrawal.status,
        'gateway_status': result.get('status'),
        'is_demo': result.get('is_demo', False),
    })
