

"""
Test script for OTP Verification System
Run: python test_otp_system.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'survey_rewards_site.settings')
django.setup()

from django.test import TestCase, Client
from django.urls import reverse
from users.models import User, OTPVerification
from captcha.models import CaptchaStore

class OTPTestCase(TestCase):
    """Test the OTP system"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create a test user
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            is_verified=False
        )
        
        # Create a captcha
        self.captcha = CaptchaStore.objects.create(
            challenge='abc123',
            response='abc123'
        )
    
    def test_otp_creation(self):
        """Test that OTP can be created for user"""
        from users.otp_utils import create_email_otp
        
        otp_record = create_email_otp(self.user)
        
        self.assertEqual(otp_record.user, self.user)
        self.assertEqual(len(otp_record.otp_code), 6)
        self.assertFalse(otp_record.is_verified)
        print(f"✓ OTP created: {otp_record.otp_code}")
    
    def test_otp_verification_success(self):
        """Test successful OTP verification"""
        from users.otp_utils import create_email_otp, verify_otp
        
        otp_record = create_email_otp(self.user)
        is_valid, message = verify_otp(otp_record, otp_record.otp_code)
        
        self.assertTrue(is_valid)
        self.assertTrue(otp_record.is_verified)
        print(f"✓ OTP verification successful: {message}")
    
    def test_otp_verification_failure(self):
        """Test failed OTP verification"""
        from users.otp_utils import create_email_otp, verify_otp
        
        otp_record = create_email_otp(self.user)
        is_valid, message = verify_otp(otp_record, '000000')
        
        self.assertFalse(is_valid)
        self.assertEqual(otp_record.attempts, 1)
        print(f"✓ OTP verification failed (expected): {message}")
    
    def test_otp_expiry(self):
        """Test OTP expiry"""
        from users.otp_utils import create_email_otp
        from django.utils import timezone
        import datetime
        
        otp_record = create_email_otp(self.user)
        
        # Manually set created_at to 15 minutes ago
        otp_record.created_at = timezone.now() - datetime.timedelta(minutes=15)
        otp_record.save()
        
        self.assertTrue(otp_record.is_expired())
        print("✓ OTP expiry detection working")
    
    def test_resend_otp_cooldown(self):
        """Test OTP resend cooldown"""
        from users.otp_utils import create_email_otp, resend_otp
        
        otp_record = create_email_otp(self.user)
        otp_record2, message = resend_otp(self.user, 'email')
        
        # Should be None due to cooldown
        self.assertIsNone(otp_record2)
        self.assertIn('wait', message.lower())
        print(f"✓ Resend cooldown working: {message}")
    
    def test_registration_redirect(self):
        """Test registration redirects to OTP verification"""
        response = self.client.get(reverse('verify_otp'))
        
        # Should redirect because no pending user in session
        self.assertEqual(response.status_code, 302)
        print("✓ Registration flow redirects correctly")
    
    def test_user_model(self):
        """Test user model fields"""
        self.assertFalse(self.user.is_verified)
        self.assertIsNotNone(self.user.referral_code)
        print(f"✓ User model working (referral code: {self.user.referral_code})")


def run_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("Testing OTP Verification System")
    print("="*60 + "\n")
    
    test_case = OTPTestCase()
    test_case.setUp()
    
    tests = [
        test_case.test_otp_creation,
        test_case.test_otp_verification_success,
        test_case.test_otp_verification_failure,
        test_case.test_otp_expiry,
        test_case.test_resend_otp_cooldown,
        test_case.test_user_model,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"Results: {passed} passed, {failed} failed")
    print("="*60 + "\n")
    
    if failed == 0:
        print("🎉 All tests passed! OTP system is working correctly.")
    else:
        print(f"⚠️  {failed} test(s) failed. Please check the errors above.")


if __name__ == '__main__':
    run_tests()
