from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import JobPost,Skill
from .serializers import JobSerializer,SkillSerializer
from .models import Application, Interview, Feedback, Notification
from .serializers import ApplicationSerializer, InterviewSerializer, FeedbackSerializer, NotificationSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rbac.permissions import IsHR, IsCandidate, IsInterviewer, IsAdmin
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rbac.models import Candidate, User, Interviewer


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
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Only candidates can apply
        if getattr(request.user, 'role', None) != 'candidate':
            return Response({'detail': 'Only candidates can apply'}, status=status.HTTP_403_FORBIDDEN)

        # Use serializer to validate fields (applied_for via applied_for_id)
        serializer = ApplicationSerializer(data=request.data)
        if serializer.is_valid():
            job = serializer.validated_data['applied_for']

            try:
                candidate_instance = request.user.candidate
            except Candidate.DoesNotExist:
                return Response({'detail': 'User is authenticated but no associated Candidate profile found.'}, status=status.HTTP_400_BAD_REQUEST)

            # prevent duplicate
            if Application.objects.filter(applied_by=candidate_instance, applied_for=job).exists():
                return Response({'detail': 'Already applied'}, status=status.HTTP_400_BAD_REQUEST)

            # create application and attach resume if provided
            resume_file = request.FILES.get('resume')
            app = Application.objects.create(
                description=serializer.validated_data.get('description', ''),
                applied_by=candidate_instance,
                applied_for=job,
                resume=resume_file
            )
            out = ApplicationSerializer(app, context={'request': request})
            return Response(out.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HRApplicationListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if getattr(request.user, 'role', None) != 'hr':
            return Response({'detail': 'Only HR can view applications'}, status=status.HTTP_403_FORBIDDEN)

        apps = Application.objects.all()
        serializer = ApplicationSerializer(apps, many=True, context={'request': request})
        return Response(serializer.data)


class CandidateApplicationListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if getattr(request.user, 'role', None) != 'candidate':
            return Response({'detail': 'Only candidates can view their applications'}, status=status.HTTP_403_FORBIDDEN)
        try:
            candidate = request.user.candidate
        except Exception:
            return Response({'detail': 'Candidate profile not found'}, status=status.HTTP_400_BAD_REQUEST)

        apps = Application.objects.filter(applied_by=candidate).order_by('-applied_date')
        serializer = ApplicationSerializer(apps, many=True, context={'request': request})
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

        return Response(ApplicationSerializer(app, context={'request': request}).data)





class ScheduleInterviewAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if getattr(request.user, 'role', None) != 'hr':
            return Response({'detail': 'Only HR can schedule interviews'}, status=status.HTTP_403_FORBIDDEN)

        serializer = InterviewSerializer(data=request.data)
        if serializer.is_valid():
            application = serializer.validated_data['application']
            interviewer_id = request.data.get('interviewer')
            
            interviewer_instance = None 

            if interviewer_id:
               
                base_user = get_object_or_404(User, id=interviewer_id, role='interviewer')
                
                
                try:
                    interviewer_instance = base_user.interviewer 
                except Interviewer.DoesNotExist:
                    return Response({'detail': 'Interviewer user found but no associated Interviewer profile.'}, status=status.HTTP_400_BAD_REQUEST)
                


            interview = Interview.objects.create(
                application=application,
                interviewer=interviewer_instance, # <-- FIX: Assign the specific Interviewer instance
                date=serializer.validated_data['date'],
                start_time=serializer.validated_data['start_time'],
                duration=serializer.validated_data['duration']
            )

            Notification.objects.create(user=application.applied_by, message=f"Interview scheduled for {application.applied_for.title} on {interview.date}")
            return Response(InterviewSerializer(interview).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)






class InterviewerFeedbackAPIView(APIView):
    # ... (permission check omitted) ...

    def post(self, request, interview_id):
        if getattr(request.user, 'role', None) != 'interviewer':
            return Response({'detail': 'Only Interviewers can add feedback'}, status=status.HTTP_403_FORBIDDEN)

        interview = get_object_or_404(Interview, id=interview_id)
        serializer = FeedbackSerializer(data=request.data)
        if serializer.is_valid():
            
            
            try:
                interviewer_instance = request.user.interviewer
            except Interviewer.DoesNotExist:
                return Response({'detail': 'User is authenticated but no associated Interviewer profile found.'}, status=status.HTTP_400_BAD_REQUEST)
            
            
            feedback = Feedback.objects.create(
                feedback=serializer.validated_data['feedback'],
                rating=serializer.validated_data['rating'],
                reviewer=interviewer_instance 
            )
            interview.feedback = feedback
            interview.save()

            Notification.objects.create(user=interview.application.applied_by, message=f"Feedback added for your interview on {interview.date}")
            return Response(FeedbackSerializer(feedback).data, status=status.HTTP_201_CREATED)


class InterviewsListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # If interviewer, return only their assigned interviews
        if getattr(request.user, 'role', None) == 'interviewer':
            try:
                interviewer = request.user.interviewer
            except Interviewer.DoesNotExist:
                return Response({'detail': 'Interviewer profile not found'}, status=status.HTTP_400_BAD_REQUEST)
            interviews = Interview.objects.filter(interviewer=interviewer).order_by('-date')
        elif getattr(request.user, 'role', None) == 'hr':
            interviews = Interview.objects.all().order_by('-date')
        else:
            # Candidates can see their own interviews
            try:
                candidate = request.user.candidate
                interviews = Interview.objects.filter(application__applied_by=candidate).order_by('-date')
            except Exception:
                return Response({'detail': 'Not authorized to view interviews'}, status=status.HTTP_403_FORBIDDEN)

        serializer = InterviewSerializer(interviews, many=True, context={'request': request})
        return Response(serializer.data)

class NotificationListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notes = Notification.objects.filter(user=request.user).order_by('-created_at')
        serializer = NotificationSerializer(notes, many=True)
        return Response(serializer.data)


class NotificationMarkReadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, note_id):
        note = get_object_or_404(Notification, id=note_id, user=request.user)
        note.is_read = True
        note.save()
        serializer = NotificationSerializer(note)
        return Response(serializer.data)
