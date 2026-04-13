from django.contrib import admin
from .models import Survey, SurveyAnswer, SurveyQuestion

@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'reward', 'estimated_time', 'is_active', 'current_participants', 'created_at']
    list_filter = ['category', 'difficulty', 'is_active']
    search_fields = ['title', 'description']

@admin.register(SurveyQuestion)
class SurveyQuestionAdmin(admin.ModelAdmin):
    list_display = ['survey', 'question_text', 'question_type', 'order']
    list_filter = ['question_type']

@admin.register(SurveyAnswer)
class SurveyAnswerAdmin(admin.ModelAdmin):
    list_display = ['user', 'survey', 'reward_earned', 'completed_at']
    list_filter = ['completed_at']
    search_fields = ['user__email', 'survey__title']
