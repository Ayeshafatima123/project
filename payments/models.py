from django.db import models
from django.conf import settings
from django.utils import timezone


class WithdrawalMethod(models.Model):
    """Available withdrawal methods"""
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, help_text="Icon class or emoji")
    min_amount = models.DecimalField(max_digits=10, decimal_places=2, default=5.00)
    max_amount = models.DecimalField(max_digits=10, decimal_places=2, default=1000.00)
    processing_time = models.CharField(max_length=100, help_text="e.g., '24-48 hours'")
    fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, help_text="Fee percentage charged")
    is_active = models.BooleanField(default=True)
    instructions = models.TextField(blank=True, help_text="Instructions for users")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Withdrawal(models.Model):
    """Withdrawal requests"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='withdrawals')
    method = models.ForeignKey(WithdrawalMethod, on_delete=models.PROTECT, related_name='withdrawals')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Amount after fee")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Payment details
    account_number = models.CharField(max_length=100, help_text="Account/Wallet number")
    account_name = models.CharField(max_length=200, help_text="Account holder name")
    payment_details = models.JSONField(help_text="Additional payment details")
    
    # Tracking
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    admin_notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - ${self.amount} ({self.status})"

    def save(self, *args, **kwargs):
        if not self.net_amount:
            self.net_amount = self.amount - self.fee
        super().save(*args, **kwargs)


class Transaction(models.Model):
    """All transactions (earnings and withdrawals)"""
    TYPE_CHOICES = [
        ('survey_reward', 'Survey Reward'),
        ('referral_bonus', 'Referral Bonus'),
        ('bonus', 'Bonus'),
        ('withdrawal', 'Withdrawal'),
        ('refund', 'Refund'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    balance_after = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255)
    reference_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.type} - ${self.amount}"


class RewardGiftCard(models.Model):
    """Gift card rewards"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='gift_cards')
    brand = models.CharField(max_length=100)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    cost_points = models.DecimalField(max_digits=10, decimal_places=2, help_text="Balance required")
    code = models.CharField(max_length=100, blank=True, null=True)
    is_redeemed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    redeemed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.brand} - ${self.value}"
