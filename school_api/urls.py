from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from apps.authentication.views import CustomTokenObtainPairView, SendEmailCodeConfirmation, ConfirmCodeEmail
from apps.administrator.views import home_page_view
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from apps.authentication.views import CreateUserView

schema_view = get_schema_view(
    openapi.Info(
        title="API SCHOOL",
        default_version='v1',
        description="Documentación de la API"
    ),
    public=True,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_page_view, name="home"),
    path('api/token/', CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('ad/', include('apps.administrator.urls')),
    path('student/', include('apps.student.urls')),
    path('teacher/', include('apps.teacher.urls')),
    path('tutor/', include('apps.tutor.urls')),
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-ui'),
    path('api/docs/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('getcode/', SendEmailCodeConfirmation.as_view(), name='getcode'),
    path('resetpassword/', ConfirmCodeEmail.as_view(), name='resetpassword'),
    path('create-superuser/', CreateUserView.as_view(), name='create_superuser'),
]
