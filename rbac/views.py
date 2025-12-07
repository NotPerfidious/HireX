from django.shortcuts import render

# Create your views here.
from rest_framework.generics import CreateAPIView
from .serializers import UserSignupSerializer
from .models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import ForgotPasswordSerializer, ResetPasswordSerializer
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model

from .serializers import LoginSerializer
from rest_framework.permissions import IsAuthenticated
from .permissions import IsAdmin
from rest_framework import status

from .serializers import UserSignupSerializer

class SignupAPIView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSignupSerializer
    
    def get_serializer(self, *args, **kwargs):
        # Allow creating any role (admin/hr/interviewer) from this endpoint
        kwargs.setdefault('context', {})
        kwargs['context']['admin_create'] = True
        return super().get_serializer(*args, **kwargs)



class LoginAPIView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "role": user.role,
            "email": user.email
        })


User = get_user_model()

class ForgotPasswordAPIView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"message": "Email not found"}, status=404)

        token = default_token_generator.make_token(user)

        # Send token by email (you integrate later)
        return Response({
            "message": "Password reset token generated",
            "token": token
        })
    
class ResetPasswordAPIView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']

        for user in User.objects.all():
            if default_token_generator.check_token(user, token):
                user.set_password(new_password)
                user.save()
                return Response({"message": "Password reset successful"})

        return Response({"error": "Invalid or expired token"}, status=400)


class AdminCreateUserAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request):
        # Admin can create HR or Interviewer (or admin) users
        serializer = UserSignupSerializer(data=request.data, context={'admin_create': True})
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AdminDeleteUserAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def delete(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        user.delete()
        return Response({'detail': 'User deleted'}, status=status.HTTP_204_NO_CONTENT)


class AdminListUsersAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        users = User.objects.all().order_by('id')
        from .serializers import AdminUserSerializer
        serializer = AdminUserSerializer(users, many=True)
        return Response(serializer.data)


class CandidateProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            candidate = request.user.candidate
        except Exception:
            return Response({'detail': 'Candidate profile not found'}, status=status.HTTP_404_NOT_FOUND)
        from .serializers import CandidateSerializer
        serializer = CandidateSerializer(candidate)
        return Response(serializer.data)

    def put(self, request):
        try:
            candidate = request.user.candidate
        except Exception:
            return Response({'detail': 'Candidate profile not found'}, status=status.HTTP_404_NOT_FOUND)
        from .serializers import CandidateSerializer
        serializer = CandidateSerializer(candidate, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
