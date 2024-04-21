from rest_framework import serializers
from .models import CompletedLesson, Course, Enrollment, Module, Lesson, Category, UserCart
# from django.contrib.auth.models import CustomUser
# from django.contrib.auth import get_user_model, authenticate

# from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from rest_framework.serializers import ValidationError
from rest_framework.authtoken.models import Token

UserModel = get_user_model()

class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = '__all__'

    def create(self, validated_data):
        user_obj = UserModel.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            # role=validated_data['role']
        )
        user_obj.save()
        return user_obj

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def check_user(self, clean_data):
        user = authenticate(username=clean_data['email'], password=clean_data['password'])
        if not user:
            raise ValidationError('User not found')
        return user

class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = UserModel
		# fields = ('email', 'username','password')
		fields = '__all__'
  
class UserProfileEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields ='__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        # fields = ['category', 'course']
        fields = '__all__'
        
class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        # fields = ['category', 'course']
        fields = '__all__'

class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = '__all__'
class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'
        
class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = '__all__'

class CompletedLessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompletedLesson
        fields = '__all__'
        
class UserCartSerializer(serializers.ModelSerializer):
    class Meta:
        model=UserCart 
        fields = '__all__'
        # exclude=['user']
        