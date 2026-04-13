from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.conf import settings
import datetime


class User(AbstractUser):
    """Custom User model with balance tracking"""
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_earned = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_withdrawn = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_verified = models.BooleanField(default=False)
    referral_code = models.CharField(max_length=20, unique=True, blank=True, null=True)
    referred_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='referrals')
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"{self.email} - ${self.balance}"

    def save(self, *args, **kwargs):
        if not self.referral_code:
            import uuid
            self.referral_code = str(uuid.uuid4())[:8].upper()
        super().save(*args, **kwargs)


class UserProfile(models.Model):
    """Extended user profile"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    country = models.CharField(max_length=100, default='Pakistan')
    city = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    completed_surveys = models.IntegerField(default=0)
    referral_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email}'s Profile"


class OTPVerification(models.Model):
    """OTP Verification model for email/phone verification"""
    OTP_TYPE_CHOICES = [
        ('email', 'Email'),
        ('phone', 'Phone'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otp_verifications')
    otp_code = models.CharField(max_length=10)
    otp_type = models.CharField(max_length=10, choices=OTP_TYPE_CHOICES, default='email')
    sent_to = models.CharField(max_length=255)  # Email or phone number
    is_verified = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.email} - {self.otp_type} OTP"
    
    def is_expired(self):
        """Check if OTP has expired"""
        expiry_minutes = getattr(settings, 'OTP_EXPIRY_MINUTES', 10)
        expiry_time = self.created_at + datetime.timedelta(minutes=expiry_minutes)
        return timezone.now() > expiry_time
    
    def can_resend(self):
        """Check if OTP can be resent (1 minute cooldown)"""
        return (timezone.now() - self.created_at).total_seconds() >= 60
    
    class Meta:
        ordering = ['-created_at']
