from rest_framework import serializers
from .models import JobPost, Skill 
from .models import Application, Interview, Feedback, Notification
from django.utils import timezone

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name']

class JobSerializer(serializers.ModelSerializer):
    skills = SkillSerializer(many=True, read_only=True)
    skill_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Skill.objects.all(),
        write_only=True,
        source='skills'  
    )

    class Meta:
        model = JobPost
        fields = [
            'id', 'title', 'description', 
            'skills',       # read-only nested
            'skill_ids',    # write-only IDs
            'posted_date', 'is_active'
        ]
        read_only_fields = ['id', 'posted_date']


class ApplicationSerializer(serializers.ModelSerializer):
    applied_by = serializers.StringRelatedField(read_only=True)
    applied_for = JobSerializer(read_only=True)
    applied_for_id = serializers.PrimaryKeyRelatedField(
        queryset=JobPost.objects.all(), write_only=True, source='applied_for'
    )

    class Meta:
        model = Application
        fields = ['id', 'description', 'applied_by', 'applied_for', 'applied_for_id', 'status', 'applied_date']
        read_only_fields = ['id', 'applied_by', 'status', 'applied_date']


class FeedbackSerializer(serializers.ModelSerializer):
    reviewer = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Feedback
        fields = ['id', 'feedback', 'rating', 'reviewer', 'created_at']
        read_only_fields = ['id', 'reviewer', 'created_at']


class InterviewSerializer(serializers.ModelSerializer):
    application = ApplicationSerializer(read_only=True)
    application_id = serializers.PrimaryKeyRelatedField(
        queryset=Application.objects.all(), write_only=True, source='application'
    )
    # Accept interviewer id in write operations
    interviewer = serializers.IntegerField(required=False, allow_null=True, write_only=True)

    class Meta:
        model = Interview
        fields = ['id', 'application', 'application_id', 'interviewer', 'date', 'start_time', 'duration', 'feedback']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user', 'message', 'is_read', 'created_at']
        read_only_fields = ['id', 'created_at']
