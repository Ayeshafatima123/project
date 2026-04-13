from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from .models import Survey, SurveyAnswer, SurveyQuestion
from users.models import User


def survey_list(request):
    """List all available surveys"""
    surveys = Survey.objects.filter(is_active=True)
    
    # Filter out completed surveys if user is authenticated
    if request.user.is_authenticated:
        completed_ids = request.user.survey_answers.values_list('survey_id', flat=True)
        surveys = surveys.exclude(id__in=completed_ids)
    
    context = {
        'surveys': surveys,
    }
    return render(request, 'surveys/survey_list.html', context)


def survey_detail(request, survey_id):
    """Survey details page - accessible without login"""
    survey = get_object_or_404(Survey, id=survey_id, is_active=True)
    questions = survey.questions.all()
    
    # Check if user has already completed this survey
    already_completed = False
    if request.user.is_authenticated:
        already_completed = SurveyAnswer.objects.filter(
            user=request.user, 
            survey=survey
        ).exists()

    context = {
        'survey': survey,
        'questions': questions,
        'is_available': survey.is_available,
        'already_completed': already_completed,
    }
    return render(request, 'surveys/survey_detail.html', context)


def start_survey(request, survey_id):
    """Start a survey - redirects to login if not authenticated"""
    if not request.user.is_authenticated:
        from django.contrib.auth.views import redirect_to_login
        return redirect_to_login(request.get_full_path(), login_url='login')
    
    survey = get_object_or_404(Survey, id=survey_id, is_active=True)

    # Check if already completed
    if SurveyAnswer.objects.filter(user=request.user, survey=survey).exists():
        messages.warning(request, 'You have already completed this survey.')
        return redirect('survey_list')

    questions = survey.questions.all()

    context = {
        'survey': survey,
        'questions': questions,
    }
    return render(request, 'surveys/survey_start.html', context)


@login_required
def submit_survey(request, survey_id):
    """Submit survey answers"""
    survey = get_object_or_404(Survey, id=survey_id, is_active=True)
    
    if request.method != 'POST':
        return redirect('survey_list')
    
    # Check if already completed
    if SurveyAnswer.objects.filter(user=request.user, survey=survey).exists():
        messages.warning(request, 'You have already completed this survey.')
        return redirect('survey_list')
    
    questions = survey.questions.all()
    answers = {}
    
    # Collect answers
    for question in questions:
        answer_key = f'question_{question.id}'
        if answer_key in request.POST:
            answers[str(question.id)] = request.POST.get(answer_key)
    
    # Save survey answer
    with transaction.atomic():
        survey_answer = SurveyAnswer.objects.create(
            survey=survey,
            user=request.user,
            answer_data=answers,
            reward_earned=survey.reward
        )
        
        # Update user balance
        request.user.balance += survey.reward
        request.user.total_earned += survey.reward
        request.user.profile.completed_surveys += 1
        request.user.profile.save()
        request.user.save()
        
        # Update survey participants
        survey.current_participants += 1
        survey.save()
        
        # Create transaction record
        from payments.models import Transaction
        Transaction.objects.create(
            user=request.user,
            type='survey_reward',
            amount=survey.reward,
            balance_after=request.user.balance,
            description=f'Completed: {survey.title}'
        )
        
        # Check for referral bonus
        if request.user.referred_by:
            referral_bonus = 0.10  # 10% of reward
            request.user.referred_by.balance += referral_bonus
            request.user.referred_by.total_earned += referral_bonus
            request.user.referred_by.profile.referral_earnings += referral_bonus
            request.user.referred_by.profile.save()
            request.user.referred_by.save()
            
            Transaction.objects.create(
                user=request.user.referred_by,
                type='referral_bonus',
                amount=referral_bonus,
                balance_after=request.user.referred_by.balance,
                description=f'Referral earnings from {request.user.email}'
            )
    
    messages.success(request, f'Survey completed! You earned ${survey.reward}')
    return redirect('dashboard')
