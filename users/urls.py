from django.urls import path
from .views import *

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('signup/', SignInView.as_view(), name='signup'),
    path('mfa-setup/', MFASetupView.as_view(), name='mfa-setup'),
    path('mfa-validate/', MFAValidateView.as_view(), name='mfa-validate'),
    path('mfa-disable/', MFADisableView.as_view(), name='mfa-disable'),
    path('mfa-activate/', MFAActivateView.as_view(), name='mfa-activate')
]
