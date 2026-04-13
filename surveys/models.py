from django.db import models
from django.conf import settings
from django.utils import timezone


class Survey(models.Model):
    """Survey model with reward information"""
    CATEGORY_CHOICES = [
        ('health', 'Health & Wellness'),
        ('tech', 'Technology'),
        ('shopping', 'Shopping'),
        ('finance', 'Finance'),
        ('education', 'Education'),
        ('entertainment', 'Entertainment'),
        ('food', 'Food & Dining'),
        ('travel', 'Travel'),
        ('general', 'General'),
    ]

    DIFFICULTY_CHOICES = [
        ('easy', 'Easy (2-5 mins)'),
        ('medium', 'Medium (5-10 mins)'),
        ('hard', 'Hard (10-20 mins)'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='general')
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='easy')
    reward = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_time = models.IntegerField(help_text="Estimated time in minutes")
    questions_count = models.IntegerField(default=10)
    is_active = models.BooleanField(default=True)
    max_participants = models.IntegerField(null=True, blank=True)
    current_participants = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} - ${self.reward}"

    @property
    def is_available(self):
        if not self.is_active:
            return False
        if self.max_participants and self.current_participants >= self.max_participants:
            return False
        if self.expires_at and timezone.now() > self.expires_at:
            return False
        return True


class SurveyAnswer(models.Model):
    """Individual survey answer"""
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='answers')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='survey_answers')
    answer_data = models.JSONField(help_text="Store answers as JSON")
    completed_at = models.DateTimeField(auto_now_add=True)
    reward_earned = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ['survey', 'user']
        ordering = ['-completed_at']

    def __str__(self):
        return f"{self.user.email} - {self.survey.title}"


class SurveyQuestion(models.Model):
    """Survey question"""
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=50, choices=[
        ('multiple_choice', 'Multiple Choice'),
        ('text', 'Text Answer'),
        ('rating', 'Rating (1-5)'),
        ('yes_no', 'Yes/No'),
    ], default='multiple_choice')
    options = models.JSONField(null=True, blank=True, help_text="For multiple choice questions")
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Q{self.order}: {self.question_text[:50]}"
