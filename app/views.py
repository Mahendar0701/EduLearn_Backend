from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from django.http import HttpResponse

from django.shortcuts import get_object_or_404, render
from rest_framework.views import APIView
from . models import *
from .models import Course, Module

from rest_framework.response import Response
from . serializer import *
from . serializer import CourseSerializer, ModuleSerializer, UserSerializer,LessonSerializer
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate, login, get_user_model
# from django.http import JsonResponse
from rest_framework import generics
from rest_framework.permissions import AllowAny
from django.contrib.auth.hashers import check_password

from django.contrib.auth import get_user_model, login, logout
from rest_framework.authentication import SessionAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from . serializer import UserRegisterSerializer, UserLoginSerializer, UserSerializer,UserProfileEditSerializer
from rest_framework import permissions, status
from .validations import custom_validation, validate_email, validate_password
from rest_framework.authtoken.models import Token

from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt

from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import BasePermission


# Create your views here.

class UserRegisterView(APIView):
	permission_classes = (permissions.AllowAny,)
	def post(self, request):
		clean_data = custom_validation(request.data)
		serializer = UserRegisterSerializer(data=clean_data)
		if serializer.is_valid(raise_exception=True):
			user = serializer.create(clean_data)
			if user:
				return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    permission_classes = (permissions.AllowAny,)
    authentication_classes = (SessionAuthentication,)

    def post(self, request):
        data = request.data
        assert validate_email(data)
        assert validate_password(data)

        serializer = UserLoginSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.check_user(data)
            if user:
                print(f"User {user.username} authenticated successfully.")
                login(request, user)
                token, created = Token.objects.get_or_create(user=user)  # Get or create the token
                response_data = {
                    'auth_token': token.key,
                    'user': UserSerializer(user).data,
                }
                return Response(response_data, status=status.HTTP_200_OK)
        
        print("User authentication failed. Serializer errors:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLogoutView(APIView):
	permission_classes = (permissions.AllowAny,)
	authentication_classes = ()
	def post(self, request):
		logout(request)
		return Response(status=status.HTTP_200_OK)


class UserView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    # authentication_classes = (SessionAuthentication,)

    def get(self, request):
        serializer = UserSerializer(request.user)
        token, created = Token.objects.get_or_create(user=request.user)
        response_data = {
            'user': serializer.data,
            'auth_token': token.key,
        }
        return Response(response_data, status=status.HTTP_200_OK)

class AllUsersListView(ListAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    # permission_classes = [IsAuthenticated]

# @csrf_exempt
class UserProfileEditView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get(self, request):
        user = self.get_object()
        serializer = UserProfileEditSerializer(user)
        return Response(serializer.data)

    def put(self, request):
        user = self.get_object()
        serializer = UserProfileEditSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class IsCourseCreator(BasePermission):
    """
    Custom permission to only allow course creators to create, update, and delete modules and lessons.
    """

    def has_object_permission(self, request, view, obj):
        # Check if the user making the request is the creator of the course
        return obj.course.instructorId == request.user.id
    
class IsTeacher(BasePermission):
    """
    Custom permission to only allow teachers to create courses.
    """

    def has_permission(self, request, view):
        # Check if the user making the request is a teacher
        return request.user.role == 'Teacher'
    
class IsEnrolledStudent(BasePermission):
    """
    Custom permission to only allow enrolled students to view lessons and mark lessons as completed.
    """

    def has_permission(self, request, view):
        # Check if the user making the request is an enrolled student in the course
        course_id = view.kwargs.get('course_id')
        module_id = view.kwargs.get('module_id')

        # Check if the user is enrolled in the course
        enrollment = Enrollment.objects.filter(user=request.user, course_id=course_id).first()
        if not enrollment:
            return False

        # Check if the user is enrolled in the module
        if not Lesson.objects.filter(module_id=module_id, course_id=course_id).exists():
            return False

        return True


class CategoryView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    serializer_class = CategorySerializer
    
    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # @permission_classes([IsAuthenticated])
    def post(self, request):
        
        if request.user.role != 'Teacher':
            return Response({"detail": "Permission denied. you are not teacher"}, status=status.HTTP_403_FORBIDDEN)
        
        # permission_classes = [IsAuthenticated]
        self.check_permissions(request)
        serializer = CategorySerializer(data=request.data)
        
        if serializer.is_valid():
            category = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]  # Allow any user to perform GET request
        return [IsAuthenticated()]
    
class CourseView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly, IsTeacher]
    
    serializer_class = CourseSerializer
    
    def get(self, request):
        courses = Course.objects.all()
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # @permission_classes([IsAuthenticated])
    def post(self, request):
        
        if request.user.role != 'Teacher':
            return Response({"detail": "Permission denied. you are not teacher"}, status=status.HTTP_403_FORBIDDEN)
        
        # permission_classes = [IsAuthenticated]
        self.check_permissions(request)
        serializer = CourseSerializer(data=request.data)
        
        if serializer.is_valid():
            # print("--------------",request.user)
            serializer.validated_data['instructorId'] = request.user.user_id
            course = serializer.save()
            Enrollment.objects.create(user=request.user, course=course)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]  # Allow any user to perform GET request
        return [IsAuthenticated()]

class CourseDetailView(APIView):
    
    permission_classes = [IsAuthenticatedOrReadOnly]
    # permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        course = Course.objects.get(pk=pk)
        serializer = CourseSerializer(course)
        return Response(serializer.data)
    
    def put(self, request, pk):
        # self.check_permissions(request)
        course = get_object_or_404(Course, id=pk)
        if course.instructorId != request.user.user_id:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            course = Course.objects.get(pk=pk)
            serializer = CourseSerializer(course, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Course.DoesNotExist:
            return Response(
                {"detail": "Course not found."},
                status=status.HTTP_404_NOT_FOUND
            )
    def delete(self, request, pk):
        course = get_object_or_404(Course, id=pk)
        if course.instructorId != request.user.user_id:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            course = Course.objects.get(pk=pk)
            course.delete()
            return Response({"detail": "Course deleted successfully."})

        except Course.DoesNotExist:
            return Response(
                {"detail": "Course not found."},
                status=status.HTTP_404_NOT_FOUND
            )
            
    
    
class ModuleList(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get(self, request, course_id):
        modules = Module.objects.filter(course_id=course_id).order_by("order")
        serializer = ModuleSerializer(modules, many=True)
        # course = Course.objects.get(pk=course_id)
        # course.num_modules = modules.count()
        # course.save()
        return Response(serializer.data)
    


    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        if course.instructorId != request.user.user_id:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        
        data = request.data.copy()
        data['course'] = course_id
        serializer = ModuleSerializer(data=data)
        if serializer.is_valid():
            serializer.validated_data['instructorId'] = request.user.user_id
            serializer.save()
            course = Course.objects.get(pk=course_id)
            course.num_modules = Module.objects.filter(course=course).count()
            course.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class ModuleDetailView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, course_id, pk):
        try:
            module = Module.objects.get(course_id=course_id, pk=pk)
            serializer = ModuleSerializer(module)
            return Response(serializer.data)
        except Module.DoesNotExist:
            return Response({"detail": "Module not found"}, status=status.HTTP_404_NOT_FOUND)
        
    def put(self, request, course_id, pk):
        course = get_object_or_404(Course, id=course_id)
        if course.instructorId != request.user.user_id:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            module = Module.objects.get(course_id=course_id, pk=pk)
            serializer = ModuleSerializer(module, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Module.DoesNotExist:
            return Response({"detail": "Module not found"}, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, course_id, pk):
        course = get_object_or_404(Course, id=course_id)
        if course.instructorId != request.user.user_id:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            module = Module.objects.get(course_id=course_id, pk=pk)
        except Module.DoesNotExist:
            return Response({"detail": "Module not found"}, status=status.HTTP_404_NOT_FOUND)

        module.delete()
        return Response({"detail": "Module deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        
class LessonList(APIView):
    # permission_classes = [IsAuthenticatedOrReadOnly]
    permission_classes = [IsAuthenticated]
    def get(self, request, course_id, module_id):
        
        
        enrollment = Enrollment.objects.filter(user=request.user, course_id=course_id).first()
        if not enrollment:
            return Response({"detail": "Permission denied. User is not enrolled in this course."}, status=status.HTTP_403_FORBIDDEN)
        
        lessons = Lesson.objects.filter(module__course_id=course_id, module_id=module_id)

        serializer = LessonSerializer(lessons, many=True)
        
        course = Course.objects.get(pk=course_id)
        course.num_lessons = lessons.count()
        course.save()
        
        module = Module.objects.get(pk=module_id)
        module.num_lessons = lessons.count()
        module.save()
        
        return Response(serializer.data)

    def post(self, request, course_id, module_id):
        course = get_object_or_404(Course, id=course_id)
        if course.instructorId != request.user.user_id:
            return Response({"detail": "Permission denied. you are not creator"}, status=status.HTTP_403_FORBIDDEN)
        data = request.data.copy()
        
        data['module'] = module_id
        serializer = LessonSerializer(data=data)
        if serializer.is_valid():
            serializer.validated_data['instructorId'] = request.user.user_id
            serializer.save()
            
            course = Course.objects.get(pk=course_id)
            course.num_lessons = Lesson.objects.filter(module__course=course).count()
            course.save()
            
            module = Module.objects.get(pk=module_id)
            module.num_lessons = Lesson.objects.filter(module=module).count()
            module.save()
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LessonDetail(APIView):
    permission_classes = [IsAuthenticated]
    # @csrf_exempt  # Only use this decorator if CSRF protection is enabled
    def put(self, request, course_id, module_id, pk):
        course = get_object_or_404(Course, id=course_id)
        if course.instructorId != request.user.user_id:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            lesson = Lesson.objects.get(module__course_id=course_id, module_id=module_id, pk=pk)
        except Lesson.DoesNotExist:
            return Response({"detail": "Lesson not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = LessonSerializer(lesson, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # @csrf_exempt  # Only use this decorator if CSRF protection is enabled
    def options(self, request, course_id, module_id, pk):
        # Allow OPTIONS requests
        response = HttpResponse()
        response["allow"] = "PUT, OPTIONS"
        return response

    def get(self, request, course_id, module_id, pk):
        enrollment = Enrollment.objects.filter(user=request.user, course_id=course_id).first()
        if not enrollment:
            return Response({"detail": "Permission denied. User is not enrolled in this course."}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            lesson = Lesson.objects.get(module__course_id=course_id, module_id=module_id, pk=pk)
            serializer = LessonSerializer(lesson)
            return Response(serializer.data)
        except Lesson.DoesNotExist:
            return Response({"detail": "Lesson not found"}, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, course_id, module_id, pk):
        course = get_object_or_404(Course, id=course_id)
        if course.instructorId != request.user.user_id:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            lesson = Lesson.objects.get(module__course_id=course_id, module_id=module_id, pk=pk)
        except Lesson.DoesNotExist:
            return Response({"detail": "Lesson not found"}, status=status.HTTP_404_NOT_FOUND)

        lesson.delete()
        return Response({"detail": "Lesson deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

        
class EnrollmentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, course_id):
        user = request.user
        course = get_object_or_404(Course, id=course_id)
        enrollment = Enrollment.objects.filter(user=user, course=course).first()

        if enrollment:
            serializer = EnrollmentSerializer(enrollment)
            return Response(serializer.data)
        else:
            return Response({"detail": "User is not enrolled in this course"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, course_id):
        user = request.user
        course = get_object_or_404(Course, id=course_id)
        
        # Check if the user is already enrolled in the course
        if Enrollment.objects.filter(user=user, course=course).exists():
            return Response({"detail": "User is already enrolled in this course"}, status=status.HTTP_400_BAD_REQUEST)
        
        course.enrolledStudents += 1
        course.save()
        
        enrollment = Enrollment.objects.create(user=user, course=course)
        serializer = EnrollmentSerializer(enrollment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_enrollment(request, course_id):
    user = request.user

    try:
        course = Course.objects.get(pk=course_id)
    except Course.DoesNotExist:
        return Response({"detail": "Course not found"}, status=status.HTTP_404_NOT_FOUND)

    enrollment = Enrollment.objects.filter(user=user, course=course).exists()

    return Response(enrollment, status=status.HTTP_200_OK)



class EnrolledCoursesListView(ListAPIView):
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Enrollment.objects.filter(user=user)

class CompletedLessonView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, course_id, module_id, lesson_id):
        user = request.user
        lesson = get_object_or_404(Lesson, module__course_id=course_id, module_id=module_id, id=lesson_id)
        completed_lesson = CompletedLesson.objects.filter(user=user, lesson=lesson).first()

        if completed_lesson:
            serializer = CompletedLessonSerializer(completed_lesson)
            return Response(serializer.data)
        else:
            return Response({"detail": "Lesson is not marked as completed by this user"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, course_id, module_id, lesson_id):
        enrollment = Enrollment.objects.filter(user=request.user, course_id=course_id).first()
        if not enrollment:
            return Response({"detail": "Permission denied. User is not enrolled in this course."}, status=status.HTTP_403_FORBIDDEN)
        
        user = request.user
        lesson = get_object_or_404(Lesson, module__course_id=course_id, module_id=module_id, id=lesson_id)
        
        # Check if the lesson is already marked as completed by the user
        if CompletedLesson.objects.filter(user=user, lesson=lesson).exists():
            return Response({"detail": "Lesson is already marked as completed by this user"}, status=status.HTTP_400_BAD_REQUEST)
        
        module = lesson.module
        course = module.course
        
        completed_lesson = CompletedLesson.objects.create(user=user, lesson=lesson,module=module,course=course)
        serializer = CompletedLessonSerializer(completed_lesson)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class CompletedLessonsInCourseView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, course_id):
        enrollment = Enrollment.objects.filter(user=request.user, course_id=course_id).first()
        if not enrollment:
            return Response({"detail": "Permission denied. User is not enrolled in this course."}, status=status.HTTP_403_FORBIDDEN)
        
        user = request.user
        lessons = Lesson.objects.filter(module__course_id=course_id)
        completed_lessons = CompletedLesson.objects.filter(user=user, lesson__in=lessons)

        serializer = CompletedLessonSerializer(completed_lessons, many=True)
        return Response(serializer.data)
    
    
        
class UserCartView(APIView):
    permission_classes=[IsAuthenticated]
        
    
    def post(self,request,course_id):
        user=request.user
        course = get_object_or_404(Course, id=course_id)
        
        is_exist = UserCart.objects.filter(user=user, course=course).exists()
        
        print('----------------------------sssssss',is_exist)
        
        if(is_exist):
            return Response({"detail": "Already added to cart."})
            
        
        user_cart=UserCart.objects.create(user=user,course=course)
        
        serializer=UserCartSerializer(user_cart)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        

class UserCartDetailView(APIView):
    permission_classes=[IsAuthenticated]
    
    def get(self,request):
        
        user=request.user
        user_cart=UserCart.objects.filter(user=user)        
        serializer=UserCartSerializer(user_cart, many=True)
        
        return Response(serializer.data)
        