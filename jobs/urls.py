from django.urls import path
from .views import (
    Jobs, AddSkill, ApplyJobAPIView, HRApplicationListAPIView, CandidateApplicationListAPIView,
    ApplicationStatusUpdateAPIView, ScheduleInterviewAPIView,
    InterviewerFeedbackAPIView, NotificationListAPIView, NotificationReadAPIView, InterviewerInterviewListAPIView
)

urlpatterns = [
    path("", Jobs.as_view()),              # /jobs/  → GET (list), POST
    path("<int:id>/", Jobs.as_view()),     # /jobs/5/ → GET (single), PUT, DELETE
    path("skill/",AddSkill.as_view())
]

urlpatterns += [
    path('apply/', AddSkill.as_view(), name='apply-placeholder'),
    path('apply-job/', ApplyJobAPIView.as_view(), name='apply-job'),
    path('my-applications/', CandidateApplicationListAPIView.as_view(), name='candidate-applications'),
    path('applications/', HRApplicationListAPIView.as_view(), name='hr-applications'),
    path('applications/<int:app_id>/status/', ApplicationStatusUpdateAPIView.as_view(), name='update-application-status'),
    path('schedule-interview/', ScheduleInterviewAPIView.as_view(), name='schedule-interview'),
    path('interviews/', InterviewerInterviewListAPIView.as_view(), name='interviewer-interviews'), 
    path('interviews/<int:interview_id>/feedback/', InterviewerFeedbackAPIView.as_view(), name='interview-feedback'),
    path('notifications/', NotificationListAPIView.as_view(), name='notifications'),
    path('notifications/<int:notif_id>/read/', NotificationReadAPIView.as_view(), name='read-notification')
]
