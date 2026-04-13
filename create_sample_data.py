import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'survey_rewards_site.settings')
django.setup()

from users.models import User, UserProfile
from surveys.models import Survey, SurveyQuestion, SurveyAnswer
from payments.models import WithdrawalMethod, Transaction
from decimal import Decimal

# Create withdrawal methods
print("Creating withdrawal methods...")
methods_data = [
    {
        'name': 'JazzCash',
        'icon': '📱',
        'min_amount': Decimal('5.00'),
        'max_amount': Decimal('500.00'),
        'processing_time': '24-48 hours',
        'fee_percentage': Decimal('2.00'),
        'is_active': True,
        'instructions': 'Provide your JazzCash account number and account name'
    },
    {
        'name': 'EasyPaisa',
        'icon': '📱',
        'min_amount': Decimal('5.00'),
        'max_amount': Decimal('500.00'),
        'processing_time': '24-48 hours',
        'fee_percentage': Decimal('2.00'),
        'is_active': True,
        'instructions': 'Provide your EasyPaisa account number and account name'
    },
    {
        'name': 'PayPal',
        'icon': '💳',
        'min_amount': Decimal('10.00'),
        'max_amount': Decimal('1000.00'),
        'processing_time': '2-3 business days',
        'fee_percentage': Decimal('3.00'),
        'is_active': True,
        'instructions': 'Provide your PayPal email address'
    },
    {
        'name': 'Bank Transfer',
        'icon': '🏦',
        'min_amount': Decimal('20.00'),
        'max_amount': Decimal('2000.00'),
        'processing_time': '3-5 business days',
        'fee_percentage': Decimal('1.50'),
        'is_active': True,
        'instructions': 'Provide your bank account number, bank name, and branch'
    },
]

for method_data in methods_data:
    WithdrawalMethod.objects.get_or_create(**method_data)

print("✓ Created withdrawal methods")

# Create sample surveys
print("Creating sample surveys...")
surveys_data = [
    {
        'title': 'Consumer Shopping Habits Survey',
        'description': 'Share your shopping preferences and help brands improve their products. Answer questions about your online and offline shopping behavior.',
        'category': 'shopping',
        'difficulty': 'easy',
        'reward': Decimal('1.50'),
        'estimated_time': 5,
        'questions_count': 10,
        'is_active': True,
    },
    {
        'title': 'Health & Wellness Lifestyle',
        'description': 'Tell us about your health habits, fitness routine, and wellness preferences. Your input helps healthcare companies improve services.',
        'category': 'health',
        'difficulty': 'medium',
        'reward': Decimal('2.50'),
        'estimated_time': 8,
        'questions_count': 15,
        'is_active': True,
    },
    {
        'title': 'Technology Usage & Preferences',
        'description': 'Share how you use technology in daily life. Questions about apps, devices, and digital habits.',
        'category': 'tech',
        'difficulty': 'easy',
        'reward': Decimal('2.00'),
        'estimated_time': 6,
        'questions_count': 12,
        'is_active': True,
    },
    {
        'title': 'Food & Dining Preferences',
        'description': 'Help restaurants and food brands understand your taste preferences and dining habits.',
        'category': 'food',
        'difficulty': 'easy',
        'reward': Decimal('1.00'),
        'estimated_time': 4,
        'questions_count': 8,
        'is_active': True,
    },
    {
        'title': 'Entertainment & Media Consumption',
        'description': 'Share your viewing habits, favorite platforms, and entertainment preferences.',
        'category': 'entertainment',
        'difficulty': 'medium',
        'reward': Decimal('3.00'),
        'estimated_time': 10,
        'questions_count': 18,
        'is_active': True,
    },
    {
        'title': 'Financial Planning & Investment',
        'description': 'Help financial institutions understand your saving and investment habits. Higher reward for detailed responses.',
        'category': 'finance',
        'difficulty': 'hard',
        'reward': Decimal('5.00'),
        'estimated_time': 15,
        'questions_count': 20,
        'is_active': True,
    },
    {
        'title': 'Travel & Tourism Experience',
        'description': 'Share your travel experiences and preferences. Help travel companies improve their services.',
        'category': 'travel',
        'difficulty': 'medium',
        'reward': Decimal('2.50'),
        'estimated_time': 7,
        'questions_count': 14,
        'is_active': True,
    },
    {
        'title': 'Education & Online Learning',
        'description': 'Tell us about your learning preferences and online education experiences.',
        'category': 'education',
        'difficulty': 'easy',
        'reward': Decimal('1.50'),
        'estimated_time': 5,
        'questions_count': 10,
        'is_active': True,
    },
]

for survey_data in surveys_data:
    survey, created = Survey.objects.get_or_create(
        title=survey_data['title'],
        defaults=survey_data
    )
    if created:
        # Add sample questions
        questions = [
            {
                'question_text': 'How often do you use our products/services?',
                'question_type': 'multiple_choice',
                'options': ['Daily', 'Weekly', 'Monthly', 'Rarely'],
                'order': 1,
            },
            {
                'question_text': 'Would you recommend us to friends?',
                'question_type': 'yes_no',
                'order': 2,
            },
            {
                'question_text': 'Rate your overall satisfaction',
                'question_type': 'rating',
                'order': 3,
            },
            {
                'question_text': 'Any suggestions for improvement?',
                'question_type': 'text',
                'order': 4,
            },
        ]
        
        for q_data in questions:
            SurveyQuestion.objects.get_or_create(
                survey=survey,
                question_text=q_data['question_text'],
                defaults=q_data
            )

print(f"✓ Created {len(surveys_data)} surveys")

# Create a sample admin user if not exists
print("Creating sample admin user...")
if not User.objects.filter(email='admin@surveyrewards.com').exists():
    admin_user = User.objects.create_user(
        email='admin@surveyrewards.com',
        username='admin',
        password='admin123',
        phone='+923001234567',
        is_verified=True
    )
    UserProfile.objects.create(
        user=admin_user,
        country='Pakistan',
        city='Lahore'
    )
    admin_user.balance = Decimal('100.00')
    admin_user.total_earned = Decimal('100.00')
    admin_user.save()
    print("✓ Created admin user (admin@surveyrewards.com / admin123)")

print("\n✅ Sample data created successfully!")
print("\nLogin credentials:")
print("Email: admin@surveyrewards.com")
print("Password: admin123")
