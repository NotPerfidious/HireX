from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import JobPost,Skill
from .serializers import JobSerializer,SkillSerializer
from .models import Application, Interview, Feedback, Notification
from .serializers import ApplicationSerializer, InterviewSerializer, FeedbackSerializer, NotificationSerializer
from rest_framework.permissions import IsAuthenticated
from rbac.permissions import IsHR, IsCandidate, IsInterviewer, IsAdmin
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rbac.models import User


class Jobs(APIView):
    permission_classes = []

    def post(self, request):
        serializer = JobSerializer(data=request.data)
        # Only HR users can create job posts
        if not request.user or not request.user.is_authenticated or getattr(request.user, 'role', None) != 'hr':
            return Response({'detail': 'Only HR can create jobs'}, status=status.HTTP_403_FORBIDDEN)

        if serializer.is_valid():
            job_instance = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def get(self, request, id=None):
        if id:
            try:
                job = JobPost.objects.get(id=id)
            except JobPost.DoesNotExist:
                return Response({"error": "Job not found"}, status=status.HTTP_404_NOT_FOUND)

            serializer = JobSerializer(job)
            return Response(serializer.data)
        jobs = JobPost.objects.all()
        serialized = JobSerializer(jobs, many=True)
        return Response(serialized.data)


    def put(self, request, id):
        try:
            job = JobPost.objects.get(id=id)
        except JobPost.DoesNotExist:
            return Response({"error": "Job not found"}, status=status.HTTP_404_NOT_FOUND)

        # Only HR can update
        if not request.user or not request.user.is_authenticated or getattr(request.user, 'role', None) != 'hr':
            return Response({'detail': 'Only HR can update jobs'}, status=status.HTTP_403_FORBIDDEN)

        serializer = JobSerializer(job, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        try:
            job = JobPost.objects.get(id=id)
        except JobPost.DoesNotExist:
            return Response({"error": "Job not found"}, status=status.HTTP_404_NOT_FOUND)

        # Only HR can delete
        if not request.user or not request.user.is_authenticated or getattr(request.user, 'role', None) != 'hr':
            return Response({'detail': 'Only HR can delete jobs'}, status=status.HTTP_403_FORBIDDEN)

        job.delete()
        return Response(
            {"message": "Job deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )
    
class AddSkill(APIView):
    def post(self,request):
        serializer=SkillSerializer(data=request.data)
        if serializer.is_valid():
            skill = serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    def get(self,request):
        skills=Skill.objects.all()
        serialized=SkillSerializer(skills,many=True)
        return Response(serialized.data)


class ApplyJobAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Only candidates can apply
        if getattr(request.user, 'role', None) != 'candidate':
            return Response({'detail': 'Only candidates can apply'}, status=status.HTTP_403_FORBIDDEN)

        serializer = ApplicationSerializer(data=request.data)
        if serializer.is_valid():
            job = serializer.validated_data['applied_for']
            # prevent duplicate
            if Application.objects.filter(applied_by=request.user, applied_for=job).exists():
                return Response({'detail': 'Already applied'}, status=status.HTTP_400_BAD_REQUEST)

            app = Application.objects.create(
                description=serializer.validated_data.get('description', ''),
                applied_by=request.user,
                applied_for=job
            )
            out = ApplicationSerializer(app)
            return Response(out.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HRApplicationListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if getattr(request.user, 'role', None) != 'hr':
            return Response({'detail': 'Only HR can view applications'}, status=status.HTTP_403_FORBIDDEN)

        apps = Application.objects.all()
        serializer = ApplicationSerializer(apps, many=True)
        return Response(serializer.data)


class ApplicationStatusUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, app_id):
        if getattr(request.user, 'role', None) != 'hr':
            return Response({'detail': 'Only HR can update application status'}, status=status.HTTP_403_FORBIDDEN)

        app = get_object_or_404(Application, id=app_id)
        status_val = request.data.get('status')
        if status_val not in dict(app._meta.get_field('status').choices):
            # allow any string but prefer known statuses
            app.status = status_val
        else:
            app.status = status_val
        app.save()

        # create notification for candidate
        Notification.objects.create(user=app.applied_by, message=f"Your application for {app.applied_for.title} is now '{app.status}'")

        return Response(ApplicationSerializer(app).data)


class ScheduleInterviewAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if getattr(request.user, 'role', None) != 'hr':
            return Response({'detail': 'Only HR can schedule interviews'}, status=status.HTTP_403_FORBIDDEN)

        serializer = InterviewSerializer(data=request.data)
        if serializer.is_valid():
            application = serializer.validated_data['application']
            interviewer_id = request.data.get('interviewer')
            interviewer = None
            if interviewer_id:
                interviewer = get_object_or_404(User, id=interviewer_id, role='interviewer')

            interview = Interview.objects.create(
                application=application,
                interviewer=interviewer,
                date=serializer.validated_data['date'],
                start_time=serializer.validated_data['start_time'],
                duration=serializer.validated_data['duration']
            )

            Notification.objects.create(user=application.applied_by, message=f"Interview scheduled for {application.applied_for.title} on {interview.date}")
            return Response(InterviewSerializer(interview).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InterviewerFeedbackAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, interview_id):
        if getattr(request.user, 'role', None) != 'interviewer':
            return Response({'detail': 'Only Interviewers can add feedback'}, status=status.HTTP_403_FORBIDDEN)

        interview = get_object_or_404(Interview, id=interview_id)
        serializer = FeedbackSerializer(data=request.data)
        if serializer.is_valid():
            feedback = Feedback.objects.create(
                feedback=serializer.validated_data['feedback'],
                rating=serializer.validated_data['rating'],
                reviewer=request.user
            )
            interview.feedback = feedback
            interview.save()

            Notification.objects.create(user=interview.application.applied_by, message=f"Feedback added for your interview on {interview.date}")
            return Response(FeedbackSerializer(feedback).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NotificationListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notes = Notification.objects.filter(user=request.user).order_by('-created_at')
        serializer = NotificationSerializer(notes, many=True)
        return Response(serializer.data)
