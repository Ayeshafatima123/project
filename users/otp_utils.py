import random
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from .models import OTPVerification


def generate_otp():
    """Generate a random OTP code"""
    otp_length = getattr(settings, 'OTP_LENGTH', 6)
    return ''.join([str(random.randint(0, 9)) for _ in range(otp_length)])


def create_email_otp(user):
    """Create and send OTP to user's email"""
    # Delete any existing unverified OTPs for this user
    OTPVerification.objects.filter(user=user, is_verified=False).delete()
    
    # Generate new OTP
    otp_code = generate_otp()
    
    # Create OTP record
    otp_record = OTPVerification.objects.create(
        user=user,
        otp_code=otp_code,
        otp_type='email',
        sent_to=user.email
    )
    
    # Send email
    send_otp_email(user.email, otp_code, user.username)
    
    return otp_record


def send_otp_email(email, otp_code, username):
    """Send OTP via email"""
    subject = 'Email Verification - SurveyRewards'
    message = f'''
    Hello {username},
    
    Your OTP verification code is: {otp_code}
    
    This code will expire in {getattr(settings, 'OTP_EXPIRY_MINUTES', 10)} minutes.
    Please do not share this code with anyone.
    
    If you didn't request this code, please ignore this email.
    
    Best regards,
    SurveyRewards Team
    '''
    
    send_mail(
        subject=subject,
        message=message,
        from_email=None,  # Uses DEFAULT_FROM_EMAIL from settings
        recipient_list=[email],
        fail_silently=False,
    )


def verify_otp(otp_record, user_otp):
    """
    Verify the OTP provided by user
    Returns: (is_valid, error_message)
    """
    # Check if OTP has expired
    if otp_record.is_expired():
        return False, 'OTP has expired. Please request a new OTP.'
    
    # Check if max attempts exceeded
    if otp_record.attempts >= getattr(settings, 'OTP_MAX_ATTEMPTS', 3):
        return False, 'Maximum attempts exceeded. Please request a new OTP.'
    
    # Verify OTP code
    if otp_record.otp_code != user_otp:
        otp_record.attempts += 1
        otp_record.save(update_fields=['attempts'])
        remaining = getattr(settings, 'OTP_MAX_ATTEMPTS', 3) - otp_record.attempts
        return False, f'Invalid OTP. {remaining} attempts remaining.'
    
    # OTP is valid
    otp_record.is_verified = True
    otp_record.verified_at = timezone.now()
    otp_record.save(update_fields=['is_verified', 'verified_at'])
    
    return True, 'OTP verified successfully!'


def resend_otp(user, otp_type='email'):
    """Resend OTP to user"""
    # Check if there's a recent OTP that can be resent
    last_otp = OTPVerification.objects.filter(
        user=user,
        otp_type=otp_type,
        is_verified=False
    ).order_by('-created_at').first()
    
    # Check cooldown (1 minute)
    if last_otp and not last_otp.can_resend():
        cooldown_seconds = 60 - (timezone.now() - last_otp.created_at).total_seconds()
        return None, f'Please wait {int(cooldown_seconds)} seconds before requesting a new OTP.'
    
    # Create and send new OTP
    if otp_type == 'email':
        otp_record = create_email_otp(user)
        return otp_record, 'New OTP sent to your email.'
    
    return None, 'Invalid OTP type.'
