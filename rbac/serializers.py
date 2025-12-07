from rest_framework import serializers
from .models import User, Hr, Candidate, Interviewer, SoftwareAdmin, Company
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate

class UserSignupSerializer(serializers.ModelSerializer):
    
    company = serializers.CharField(
        required=False,
        write_only=True
    )
    
    
    class Meta:
        model=User
        fields = ['id', 'email', 'full_name', 'password', 'role', 'company']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    def create(self,validated_data):
        role = validated_data.get('role')
        
        company = validated_data.pop('company', None)
        
        validated_data['username'] = validated_data['email']
        
        # By default only allow creating candidates via public signup endpoint.
        # Views that create HR/interviewer should pass context={'admin_create': True}.
        if not self.context.get('admin_create', False) and role != 'candidate':
            raise serializers.ValidationError({'role': 'Only candidates can sign up. HR/Interviewer must be created by Admin.'})

        validated_data['password'] = make_password(validated_data['password'])

        if role == 'hr':
            # 4. PASS COMPANY OBJECT: Pass the company object to the Hr.objects.create call
            company_obj = None
            if company:
                # Basic check: if digit, try to get ID, else create by name
                if str(company).isdigit():
                    try:
                        company_obj = Company.objects.get(pk=int(company))
                    except Company.DoesNotExist:
                        pass
                
                if not company_obj:
                    company_obj, _ = Company.objects.get_or_create(name=str(company))
            else:
                 # If no company provided, use a default placeholder
                 company_obj, _ = Company.objects.get_or_create(name="Independent")

            return Hr.objects.create(company=company_obj, **validated_data) 
        elif role == 'candidate':
            # Provide default job_role to prevent 500 error
            validated_data['job_role'] = validated_data.get('job_role', 'Applicant')
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
