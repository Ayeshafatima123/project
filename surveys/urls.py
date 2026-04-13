from django.urls import path
from . import views

urlpatterns = [
    path('', views.survey_list, name='survey_list'),
    path('<int:survey_id>/', views.survey_detail, name='survey_detail'),
    path('<int:survey_id>/start/', views.start_survey, name='start_survey'),
    path('<int:survey_id>/submit/', views.submit_survey, name='submit_survey'),
]
