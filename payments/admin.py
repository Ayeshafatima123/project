from django.contrib import admin
from django.contrib import messages
from django.utils.html import format_html
from .models import WithdrawalMethod, Withdrawal, Transaction, RewardGiftCard
from .jazzcash_gateway import process_jazzcash_withdrawal
from .easypaisa_gateway import process_easypaisa_withdrawal
from .paypal_gateway import process_paypal_withdrawal


@admin.register(WithdrawalMethod)
class WithdrawalMethodAdmin(admin.ModelAdmin):
    list_display = ['name', 'min_amount', 'max_amount', 'fee_percentage', 'processing_time', 'is_active']
    list_filter = ['is_active']


@admin.register(Withdrawal)
class WithdrawalAdmin(admin.ModelAdmin):
    list_display = ['user', 'method', 'amount', 'fee', 'net_amount', 'status', 'created_at', 'payment_status_badge']
    list_filter = ['status', 'method', 'created_at']
    search_fields = ['user__email', 'account_number', 'transaction_id']
    readonly_fields = ['payment_status_badge', 'gateway_info', 'created_at', 'updated_at', 'processed_at']
    actions = ['approve_and_process_payment', 'reject_withdrawal']
    
    fieldsets = (
        ('Withdrawal Details', {
            'fields': ('user', 'method', 'amount', 'fee', 'net_amount', 'status')
        }),
        ('Payment Information', {
            'fields': ('account_number', 'account_name', 'payment_details', 'transaction_id')
        }),
        ('Status & Tracking', {
            'fields': ('payment_status_badge', 'gateway_info', 'notes', 'admin_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'processed_at'),
            'classes': ('collapse',)
        }),
    )

    @admin.display(description='Status')
    def payment_status_badge(self, obj):
        """Display status as colored badge"""
        colors = {
            'pending': '#ffc107',
            'processing': '#17a2b8',
            'completed': '#28a745',
            'rejected': '#dc3545',
            'failed': '#6c757d',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color, obj.status.upper()
        )

    @admin.display(description='Gateway Info')
    def gateway_info(self, obj):
        """Show gateway transaction info"""
        info = f'<strong>Transaction ID:</strong> {obj.transaction_id or "Not set"}<br>'
        info += f'<strong>Method:</strong> {obj.method.name}<br>'
        if obj.payment_details:
            info += f'<strong>Processing Time:</strong> {obj.payment_details.get("processing_time", "N/A")}'
        return format_html(info)

    @admin.action(description='✅ Approve & Process Real Payment')
    def approve_and_process_payment(self, request, queryset):
        """Approve withdrawal and process REAL payment"""
        processed = 0
        for withdrawal in queryset.filter(status='pending'):
            method_name = withdrawal.method.name.lower()

            # Process real payment based on method
            if 'jazzcash' in method_name:
                result = process_jazzcash_withdrawal(withdrawal)
            elif 'easypaisa' in method_name:
                result = process_easypaisa_withdrawal(withdrawal)
            elif 'paypal' in method_name:
                result = process_paypal_withdrawal(withdrawal)
            else:
                # Bank Transfer - Mark as processing (manual processing required)
                withdrawal.status = 'processing'
                withdrawal.save()
                self.message_user(
                    request,
                    f'Bank transfer #{withdrawal.id} marked as processing. Process manually.',
                    messages.INFO
                )
                processed += 1
                continue

            if result['success']:
                mode = '🔵 [DEMO] ' if result.get('is_demo') else '✅ '
                self.message_user(
                    request,
                    f'{mode}Payment sent! {result["message"]} (Txn: {result.get("transaction_id", "N/A")})',
                    messages.SUCCESS if not result.get('is_demo') else messages.INFO
                )
                processed += 1
            else:
                self.message_user(
                    request,
                    f'❌ Payment failed for #{withdrawal.id}: {result["message"]}',
                    messages.ERROR
                )
        
        if processed == 0:
            self.message_user(request, 'No pending withdrawals to process.', messages.WARNING)

    @admin.action(description='❌ Reject Withdrawal & Refund')
    def reject_withdrawal(self, request, queryset):
        """Reject withdrawal and refund user"""
        count = 0
        for withdrawal in queryset.filter(status='pending'):
            withdrawal.status = 'rejected'
            withdrawal.save()

            # Refund user balance
            user = withdrawal.user
            user.balance += withdrawal.amount
            user.save()

            Transaction.objects.create(
                user=user,
                type='refund',
                amount=withdrawal.amount,
                balance_after=user.balance,
                description=f'Refund for rejected withdrawal #{withdrawal.id}'
            )
            count += 1

        if count > 0:
            self.message_user(request, f'{count} withdrawal(s) rejected and balance refunded.', messages.WARNING)
        else:
            self.message_user(request, 'No pending withdrawals to reject.', messages.INFO)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'type', 'amount', 'balance_after', 'created_at']
    list_filter = ['type', 'created_at']
    search_fields = ['user__email', 'description']

@admin.register(RewardGiftCard)
class RewardGiftCardAdmin(admin.ModelAdmin):
    list_display = ['user', 'brand', 'value', 'cost_points', 'is_redeemed', 'created_at']
    list_filter = ['brand', 'is_redeemed']
