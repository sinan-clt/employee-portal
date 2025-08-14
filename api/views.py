from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import authenticate
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from employees.models import FormTemplate, FormField, Employee, EmployeeData
from .serializers import (
    UserSerializer, FormTemplateSerializer, FormFieldSerializer,
    EmployeeSerializer, EmployeeDataSerializer
)


@method_decorator(csrf_exempt, name='dispatch')
class UserRegisterAPIView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    'message': 'User registered successfully',
                    'user_id': user.id,
                    'email': user.email,
                    'username': user.username
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class UserLoginAPIView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        required_fields = ['email', 'password']
        if not all(field in request.data for field in required_fields):
            return Response(
                {'error': 'Missing email or password'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        email = request.data.get('email')
        password = request.data.get('password')
        
        user = authenticate(email=email, password=password)
        if user:
            from rest_framework_simplejwt.tokens import RefreshToken
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user_id': user.id,
                'email': user.email
            }, status=status.HTTP_200_OK)
        return Response(
            {'error': 'Invalid credentials'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )


@method_decorator(csrf_exempt, name='dispatch')
class FormTemplateAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        templates = FormTemplate.objects.filter(created_by=request.user)
        serializer = FormTemplateSerializer(templates, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = FormTemplateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class FormTemplateDetailAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_object(self, pk, user):
        try:
            return FormTemplate.objects.get(pk=pk, created_by=user)
        except FormTemplate.DoesNotExist:
            return None
    
    def get(self, request, pk):
        template = self.get_object(pk, request.user)
        if not template:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = FormTemplateSerializer(template)
        return Response(serializer.data)
    
    def put(self, request, pk):
        template = self.get_object(pk, request.user)
        if not template:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = FormTemplateSerializer(template, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        template = self.get_object(pk, request.user)
        if not template:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        template.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@method_decorator(csrf_exempt, name='dispatch')
class FormFieldAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_template(self, pk, user):
        try:
            return FormTemplate.objects.get(pk=pk, created_by=user)
        except FormTemplate.DoesNotExist:
            return None
    
    def get(self, request, template_pk):
        """
        List all fields for a specific form template
        """
        template = self.get_template(template_pk, request.user)
        if not template:
            return Response({'error': 'Template not found'}, status=status.HTTP_404_NOT_FOUND)
        
        fields = FormField.objects.filter(form_template=template).order_by('order')
        serializer = FormFieldSerializer(fields, many=True)
        return Response(serializer.data)
    
    def post(self, request, template_pk):
        """
        Create a new field for a form template
        """
        template = self.get_template(template_pk, request.user)
        if not template:
            return Response({'error': 'Template not found'}, status=status.HTTP_404_NOT_FOUND)
        
        data = request.data.copy()
        required_fields = ['label', 'field_type']
        
        if not all(field in data for field in required_fields):
            return Response(
                {'error': f'Missing required fields: {", ".join(required_fields)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Set automatic values
        data['form_template'] = template.pk
        data['required'] = data.get('required', True)
        
        # Calculate next order value
        last_field = FormField.objects.filter(form_template=template).order_by('-order').first()
        data['order'] = (last_field.order + 1) if last_field else 0
        
        serializer = FormFieldSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@method_decorator(csrf_exempt, name='dispatch')
class FormFieldDetailAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_object(self, template_pk, pk, user):
        try:
            return FormField.objects.get(
                pk=pk,
                form_template__pk=template_pk,
                form_template__created_by=user
            )
        except FormField.DoesNotExist:
            return None
    
    def get(self, request, template_pk, pk):
        field = self.get_object(template_pk, pk, request.user)
        if not field:
            return Response({'error': 'Field not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = FormFieldSerializer(field)
        return Response(serializer.data)
    
    def put(self, request, template_pk, pk):
        field = self.get_object(template_pk, pk, request.user)
        if not field:
            return Response({'error': 'Field not found'}, status=status.HTTP_404_NOT_FOUND)
        
        data = request.data.copy()
        if 'form_template' in data:
            data.pop('form_template')
        
        serializer = FormFieldSerializer(field, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, template_pk, pk):
        field = self.get_object(template_pk, pk, request.user)
        if not field:
            return Response({'error': 'Field not found'}, status=status.HTTP_404_NOT_FOUND)
        field.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

@method_decorator(csrf_exempt, name='dispatch')
class EmployeeAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """List all employees for the current user"""
        employees = Employee.objects.filter(created_by=request.user)
        serializer = EmployeeSerializer(employees, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        """Create a new employee"""
        serializer = EmployeeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class EmployeeDetailAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_object(self, pk, user):
        """Helper method to get employee or return None"""
        try:
            return Employee.objects.get(pk=pk, created_by=user)
        except Employee.DoesNotExist:
            return None
    
    def get(self, request, pk):
        """Get employee details"""
        employee = self.get_object(pk, request.user)
        if not employee:
            return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get basic employee data
        employee_serializer = EmployeeSerializer(employee)
        
        # Get all employee data fields
        employee_data = EmployeeData.objects.filter(employee=employee)
        data_serializer = EmployeeDataSerializer(employee_data, many=True)
        
        response_data = employee_serializer.data
        response_data['fields_data'] = data_serializer.data
        
        return Response(response_data)
    
    def put(self, request, pk):
        """Update employee details"""
        employee = self.get_object(pk, request.user)
        if not employee:
            return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = EmployeeSerializer(employee, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        """Delete an employee"""
        employee = self.get_object(pk, request.user)
        if not employee:
            return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
        
        employee.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)