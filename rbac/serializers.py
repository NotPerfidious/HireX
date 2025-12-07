from rest_framework import serializers
from .models import User, Hr, Candidate, Interviewer, SoftwareAdmin, Company
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate

class UserSignupSerializer(serializers.ModelSerializer):
    
    # Accept either a company id or a company name (string). We'll handle both
    # in create(): if the company does not exist by id or name, we'll create it.
    company = serializers.CharField(required=False, write_only=True)
    
    
    class Meta:
        model=User
        fields = ['id', 'email', 'full_name', 'password', 'role', 'company']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    def create(self,validated_data):
        role = validated_data.get('role')
        
        company_input = validated_data.pop('company', None)
        company = None
        if company_input:
            # If client sent a numeric id, try to resolve by PK first
            try:
                # allow Company instance passthrough (defensive)
                if isinstance(company_input, Company):
                    company = company_input
                else:
                    # try interpret as int primary key
                    try:
                        pk = int(company_input)
                    except Exception:
                        pk = None

                    if pk is not None:
                        try:
                            company = Company.objects.get(pk=pk)
                        except Company.DoesNotExist:
                            company = None

                    # If not found by pk, treat input as company name and get_or_create
                    if company is None:
                        company_name = str(company_input).strip()
                        if company_name:
                            company, _ = Company.objects.get_or_create(name=company_name)
            except Exception:
                # Fallback: ignore company if something goes wrong
                company = None
        
        validated_data['username'] = validated_data['email']
        
        # By default only allow creating candidates via public signup endpoint.
        # Views that create HR/interviewer should pass context={'admin_create': True}.
        if not self.context.get('admin_create', False) and role != 'candidate':
            raise serializers.ValidationError({'role': 'Only candidates can sign up. HR/Interviewer must be created by Admin.'})

        validated_data['password'] = make_password(validated_data['password'])

        if role == 'hr':
            # 4. PASS COMPANY OBJECT: Pass the company object to the Hr.objects.create call
            return Hr.objects.create(company=company, **validated_data) 
        elif role == 'candidate':
            # NOTE: Candidate model has 'job_role' which is also mandatory,
            # If this fails, we will need to add 'job_role' to the serializer next.
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


class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = ['id', 'email', 'full_name', 'job_role']
        read_only_fields = ['email']


class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'role']
        read_only_fields = ['id']
