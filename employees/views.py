from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .models import FormTemplate, FormField, Employee, EmployeeData
from django.db.models import Q
from django.core.paginator import Paginator
from .forms import CustomUserCreationForm, CustomPasswordChangeForm, ProfileUpdateForm, FormTemplateForm, FormFieldForm
import json

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'employees/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'employees/login.html', {'error': 'Invalid credentials'})
    return render(request, 'employees/login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect('profile')
    else:
        form = CustomPasswordChangeForm(request.user)
    return render(request, 'employees/change_password.html', {'form': form})

@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, 'employees/profile.html', {'form': form})

@login_required
def dashboard_view(request):
    form_count = FormTemplate.objects.filter(created_by=request.user).count()
    employee_count = Employee.objects.filter(created_by=request.user).count()
    
    return render(request, 'employees/dashboard.html', {
        'form_count': form_count,
        'employee_count': employee_count
    })

@login_required
def recent_activity_view(request):
    # Get recent form creations
    recent_forms = FormTemplate.objects.filter(
        created_by=request.user
    ).order_by('-created_at')[:5]
    
    # Get recent employee additions
    recent_employees = Employee.objects.filter(
        created_by=request.user
    ).order_by('-created_at')[:5]
    
    return render(request, 'employees/recent_activity.html', {
        'recent_forms': recent_forms,
        'recent_employees': recent_employees
    })

@login_required
def form_design_view(request):
    if request.method == 'POST':
        form = FormTemplateForm(request.POST)
        if form.is_valid():
            form_template = form.save(commit=False)
            form_template.created_by = request.user
            form_template.save()
            return redirect('form_design_edit', form_template.id)
    else:
        form = FormTemplateForm()
    
    templates = FormTemplate.objects.filter(created_by=request.user)
    return render(request, 'employees/form_design.html', {'form': form, 'templates': templates})

@login_required
def form_design_edit_view(request, template_id):
    template = get_object_or_404(FormTemplate, id=template_id, created_by=request.user)
    
    if request.method == 'POST':
        field_form = FormFieldForm(request.POST)
        if field_form.is_valid():
            field = field_form.save(commit=False)
            field.form_template = template
            field.save()
            return redirect('form_design_edit', template_id)
    else:
        field_form = FormFieldForm()
    
    fields = template.fields.all()
    return render(request, 'employees/form_design_edit.html', {
        'template': template,
        'field_form': field_form,
        'fields': fields
    })

@login_required
def employee_create_view(request, template_id):
    template = get_object_or_404(FormTemplate, id=template_id)
    fields = template.fields.all()
    
    if request.method == 'POST':
        employee = Employee.objects.create(form_template=template, created_by=request.user)
        
        for field in fields:
            value = request.POST.get(f'field_{field.id}')
            if value:
                EmployeeData.objects.create(
                    employee=employee,
                    field=field,
                    value=value
                )
        
        return redirect('employee_list')
    
    return render(request, 'employees/employee_create.html', {'template': template, 'fields': fields})

@login_required
def employee_list_view(request):
    employees = Employee.objects.filter(created_by=request.user).select_related('form_template')
    templates = FormTemplate.objects.filter(created_by=request.user)
    
    # template filter
    template_filter = request.GET.get('template')
    if template_filter and template_filter != 'all':
        employees = employees.filter(form_template_id=template_filter)
    
    # search
    search_query = request.GET.get('search')
    if search_query:
        # Search in both employee data and ID
        employees = employees.filter(
            Q(data__value__icontains=search_query) |
            Q(id__icontains=search_query)
        ).distinct()
    
    # pagination
    paginator = Paginator(employees, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'employees/employee_list.html', {
        'employees': page_obj,
        'templates': templates,
        'template_filter': template_filter,
        'search_query': search_query,
        'page_obj': page_obj,
    })

@login_required
def employee_detail_view(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id, created_by=request.user)
    return render(request, 'employees/employee_detail.html', {'employee': employee})

@login_required
def employee_delete_view(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id, created_by=request.user)
    if request.method == 'POST':
        employee.delete()
        return redirect('employee_list')
    return render(request, 'employees/employee_delete.html', {'employee': employee})

# AJAX views
@login_required
@require_http_methods(['POST'])
@csrf_exempt
def ajax_save_field_order(request):
    try:
        data = json.loads(request.body)
        for item in data:
            field = FormField.objects.get(id=item['id'], form_template__created_by=request.user)
            field.order = item['order']
            field.save()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@login_required
@require_http_methods(['DELETE'])
@csrf_exempt
def ajax_delete_field(request, field_id):
    try:
        field = FormField.objects.get(id=field_id, form_template__created_by=request.user)
        field.delete()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    

