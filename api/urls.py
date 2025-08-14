from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    UserRegisterAPIView, UserLoginAPIView,
    FormTemplateAPIView, FormTemplateDetailAPIView,
    FormFieldAPIView, FormFieldDetailAPIView,
    EmployeeAPIView, EmployeeDetailAPIView,
)

urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('register/', UserRegisterAPIView.as_view(), name='api_register'),
    path('login/', UserLoginAPIView.as_view(), name='api_login'),
    
    path('forms/', FormTemplateAPIView.as_view(), name='api_forms'),
    path('forms/<int:pk>/', FormTemplateDetailAPIView.as_view(), name='api_form_detail'),
    path('forms/<int:template_pk>/fields/', FormFieldAPIView.as_view(), name='api_fields'),
    path('forms/<int:template_pk>/fields/<int:pk>/', FormFieldDetailAPIView.as_view(), name='api_field_detail'),
    
    path('employees/', EmployeeAPIView.as_view(), name='api_employees'),
    path('employees/<int:pk>/', EmployeeDetailAPIView.as_view(), name='api_employee_detail'),
]