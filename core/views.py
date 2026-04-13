from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from surveys.models import Survey
from payments.models import Withdrawal, Transaction


def home(request):
    """Landing page"""
    surveys = Survey.objects.filter(is_active=True)[:6]
    context = {
        'surveys': surveys,
    }
    return render(request, 'core/home.html', context)


def about(request):
    """About page"""
    return render(request, 'core/about.html')


def faq(request):
    """FAQ page"""
    faqs = [
        {
            'question': 'How do I earn money?',
            'answer': 'Simply register an account, complete surveys, and earn rewards. Each survey pays between $0.50 to $5.00 depending on length and complexity.'
        },
        {
            'question': 'How do I withdraw my earnings?',
            'answer': 'You can withdraw via JazzCash, EasyPaisa, PayPal, Bank Transfer, or Gift Cards. Minimum withdrawal is $5.00.'
        },
        {
            'question': 'How long does withdrawal take?',
            'answer': 'JazzCash and EasyPaisa: 24-48 hours. PayPal: 2-3 business days. Bank Transfer: 3-5 business days.'
        },
        {
            'question': 'Is this platform legitimate?',
            'answer': 'Yes! We are a registered company working with legitimate market research firms. Your data is protected with encryption.'
        },
        {
            'question': 'How do I get more surveys?',
            'answer': 'Complete your profile, verify your email, and check back daily. We send survey invitations based on your demographics.'
        },
        {
            'question': 'Can I refer friends?',
            'answer': 'Yes! Share your referral code and earn $1.00 bonus for each friend who joins and completes their first survey.'
        },
    ]
    return render(request, 'core/faq.html', {'faqs': faqs})


def dashboard(request):
    """User dashboard - redirects to login if not authenticated"""
    if not request.user.is_authenticated:
        from django.contrib.auth.views import redirect_to_login
        return redirect_to_login(request.get_full_path(), login_url='login')
    
    user = request.user
    surveys = Survey.objects.filter(is_active=True)
    completed_surveys = user.survey_answers.count()
    available_surveys = surveys.exclude(answers__user=user)
    recent_transactions = Transaction.objects.filter(user=user)[:10]
    recent_withdrawals = Withdrawal.objects.filter(user=user)[:5]

    context = {
        'user': user,
        'balance': user.balance,
        'total_earned': user.total_earned,
        'total_withdrawn': user.total_withdrawn,
        'completed_surveys': completed_surveys,
        'available_surveys': available_surveys[:5],
        'recent_transactions': recent_transactions,
        'recent_withdrawals': recent_withdrawals,
    }
    return render(request, 'core/dashboard.html', context)
