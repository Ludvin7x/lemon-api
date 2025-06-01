from django.contrib import admin
from django.urls import include, path
from LittleLemonAPI.views import HealthCheckView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from LittleLemonAPI.views import CurrentUserView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # para obtener token
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # para refrescar token
    path('api/users/me/', CurrentUserView.as_view(), name='current_user'),

    path('api/', include('LittleLemonAPI.urls')),  
    path('healthz/', HealthCheckView.as_view(), name='health_check'),
]