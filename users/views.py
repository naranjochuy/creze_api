import pyotp
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from .serializers import *
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .models import User
from utils.common_functions import send_email


class LoginView(APIView):

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get("email")
        password = serializer.validated_data.get("password")
        user = authenticate(email=email, password=password)
        if not user:
            error = {'detail': 'Credenciales inválidas'}
            return Response(error, status=status.HTTP_401_UNAUTHORIZED)

        if user:
            refresh = RefreshToken.for_user(user)
            resp = {
                'token': str(refresh.access_token),
                'otp_activated': user.otp_activated,
                'otp_verified': user.otp_verified
            }
            return Response(resp, status=status.HTTP_200_OK)


class SignInView(APIView):

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_data = serializer.validated_data
        password = serializer.validated_data.pop('password')
        user_data |= {'otp_secret': pyotp.random_base32()}

        try:
            user = User(**user_data)
            user.set_password(password)
            user.save()
        except Exception:
            error = {'detail': 'Ha ocurrido un error inesperado'}
            return Response(error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        send_email()
        return Response(status=status.HTTP_201_CREATED)


class MFASetupView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.otp_verified:
            error = {"detail": ["Error en la petición"]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

        otp_uri = pyotp.totp.TOTP(user.otp_secret).provisioning_uri(
            name=user.email, issuer_name=settings.ISSUER_NAME
        )
        data = {"otp_uri": otp_uri}
        return Response(data, status=status.HTTP_200_OK)


class MFAValidateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = MFAValidateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data.get('code')
        user = request.user
        totp = pyotp.TOTP(user.otp_secret)
        if not totp.verify(code):
            error = {"code": ["Código OTP inválido"]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

        try:
            user.otp_verified = True
            user.save()
        except Exception:
            error = {'detail': 'Ha ocurrido un error inesperado'}
            return Response(error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if not user.recovery_codes:
            recovery_codes = user.generate_recovery_codes()
            resp = {"recovery_codes": recovery_codes}
            return Response(resp, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_200_OK)


class MFADisableView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = MFADisableSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data.get('code')
        user = request.user
        if not user.otp_activated:
            error = {"detail": ["Error en la petición"]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

        if not user.verify_recovery_code(code):
            error = {'code': 'Código inválido'}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

        try:
            user.otp_secret = None
            user.otp_activated = False
            user.otp_verified = False
            user.save()
        except Exception:
            error = {'detail': 'Ha ocurrido un error inesperado'}
            return Response(error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(status=status.HTTP_200_OK)


class MFAActivateView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = MFAActivateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        password = serializer.validated_data.get('password')

        if user.otp_activated:
            error = {"detail": ["Error en la petición"]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST,)

        if not authenticate(username=user.email, password=password):
            error = {'password': 'Contraseña inválida'}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

        try:
            user.otp_secret = pyotp.random_base32()
            user.otp_activated = True
            user.save()
        except Exception:
            error = {'detail': 'Ha ocurrido un error inesperado'}
            return Response(error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(status=status.HTTP_200_OK)
