from django.urls import path
from .views import (
    register_view, login_view, logout_view, 
    change_password_view, profile_view, recent_activity_view,
    dashboard_view, form_design_view, form_design_edit_view,
    employee_create_view, employee_list_view, employee_detail_view,
    employee_delete_view, ajax_save_field_order, ajax_delete_field
)


urlpatterns = [
    path('', dashboard_view, name='dashboard'),
    path('recent-activity/', recent_activity_view, name='recent_activity'),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('change-password/', change_password_view, name='change_password'),
    path('profile/', profile_view, name='profile'),
    
    # Form Management
    path('forms/', form_design_view, name='form_design'),
    path('forms/<int:template_id>/edit/', form_design_edit_view, name='form_design_edit'),
    
    # Employee Management
    path('forms/<int:template_id>/employee/create/', employee_create_view, name='employee_create'),
    path('employees/', employee_list_view, name='employee_list'),
    path('employees/<int:employee_id>/', employee_detail_view, name='employee_detail'),
    path('employees/<int:employee_id>/delete/', employee_delete_view, name='employee_delete'),
    
    # AJAX Endpoints
    path('ajax/save-field-order/', ajax_save_field_order, name='ajax_save_field_order'),
    path('ajax/delete-field/<int:field_id>/', ajax_delete_field, name='ajax_delete_field'),

]