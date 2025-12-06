from django.urls import path
from .views import (
    Jobs, AddSkill, ApplyJobAPIView, HRApplicationListAPIView,
    ApplicationStatusUpdateAPIView, ScheduleInterviewAPIView,
    InterviewerFeedbackAPIView, NotificationListAPIView
)

urlpatterns = [
    path("", Jobs.as_view()),              # /jobs/  → GET (list), POST
    path("<int:id>/", Jobs.as_view()),     # /jobs/5/ → GET (single), PUT, DELETE
    path("skill/",AddSkill.as_view())
]

urlpatterns += [
    path('apply/', AddSkill.as_view(), name='apply-placeholder'),
    path('apply-job/', ApplyJobAPIView.as_view(), name='apply-job'),
    path('applications/', HRApplicationListAPIView.as_view(), name='hr-applications'),
    path('applications/<int:app_id>/status/', ApplicationStatusUpdateAPIView.as_view(), name='update-application-status'),
    path('schedule-interview/', ScheduleInterviewAPIView.as_view(), name='schedule-interview'),
    path('interviews/<int:interview_id>/feedback/', InterviewerFeedbackAPIView.as_view(), name='interview-feedback'),
    path('notifications/', NotificationListAPIView.as_view(), name='notifications')
]
