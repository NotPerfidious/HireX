from rest_framework import serializers
from .models import User, Hr, Candidate, Interviewer, SoftwareAdmin
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate

class UserSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields = ['id', 'email', 'full_name', 'password', 'role']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    def create(self,validated_data):
        role = validated_data.get('role')
        # By default only allow creating candidates via public signup endpoint.
        # Views that create HR/interviewer should pass context={'admin_create': True}.
        if not self.context.get('admin_create', False) and role != 'candidate':
            raise serializers.ValidationError({'role': 'Only candidates can sign up. HR/Interviewer must be created by Admin.'})

        validated_data['password'] = make_password(validated_data['password'])

        if role == 'hr':
            return Hr.objects.create(**validated_data)
        elif role == 'candidate':
            return Candidate.objects.create(**validated_data)
        elif role == 'interviewer':
            return Interviewer.objects.create(**validated_data)
        elif role == 'admin':
            return SoftwareAdmin.objects.create(**validated_data)
        return User.objects.create(**validated_data)

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(username=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Invalid email or password")
        data['user'] = user
        return data

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField()
