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
class SignupAPIView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSignupSerializer


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
