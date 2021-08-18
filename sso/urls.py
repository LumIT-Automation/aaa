from django.urls import path

from .controllers import Root
from .controllers import Auth
from .controllers import Superadmins


urlpatterns = [
    path('api/', Root.RootController.as_view()),
    path('api/v1/', Root.RootController.as_view()),

    path('api/v1/token/', Auth.MyTokenObtainPairView.as_view(), name='token'),
    path('api/v1/token/refresh/', Auth.MyTokenObtainPairView.as_view(), name='token-refresh'),

    path('api/v1/superadmins/', Superadmins.SuperadminsController.as_view(), name='superadmins'),
]
