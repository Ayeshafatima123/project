from django.urls import path
from . import views

urlpatterns = [
    path('', views.payment_dashboard, name='payment_dashboard'),
    path('withdraw/', views.withdraw, name='withdraw'),
    path('withdraw/submit/', views.submit_withdrawal, name='submit_withdrawal'),
    path('transaction-history/', views.transaction_history, name='transaction_history'),
    # Payment gateway callbacks
    path('easypaisa/callback/', views.easypaisa_callback, name='easypaisa_callback'),
    path('easypaisa/check-status/<int:withdrawal_id>/', views.check_easypaisa_status, name='check_easypaisa_status'),
]
