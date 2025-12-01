from rest_framework import serializers
from .models import JobPost, Skill 

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
