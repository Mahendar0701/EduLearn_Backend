from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, Group, Permission
# from .models import Course

class AppUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('An email is required.')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        
        user.save()
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('An email is required.')
        user = self.create_user(email, username, password, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user
    
class Category(models.Model):
    title=models.CharField(max_length=255)


class Course(models.Model):
    COURSE_LEVEL_CHOICES = [
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
    ]
        
    title = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='courses')
    category_name = models.CharField(max_length=255,null=True,blank=True)
    description = models.TextField(max_length=500)
    image = models.TextField(max_length=1000,null=True,blank=True)
    instructorId = models.IntegerField(null=True,blank=True)
    instructor = models.CharField(max_length=255,null=True,blank=True)
    duration = models.IntegerField(null=True,blank=True)
    level = models.CharField(max_length=20, choices=COURSE_LEVEL_CHOICES,null=True,blank=True)
    num_modules = models.IntegerField(default=0)  # Number of modules in the course
    num_lessons = models.IntegerField(default=0)  # Number of lessons in the course
    price = models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)
      
    enrolledStudents = models.IntegerField(default=0)
    rating = models.FloatField(default=0,null=True,blank=True)
    startDate = models.DateField(null=True,blank=True)
    endDate = models.DateField(null=True,blank=True)
    syllabus = models.CharField(max_length=500,null=True,blank=True)
    prerequisites = models.CharField(max_length=500,null=True,blank=True)
    resources = models.CharField(max_length=500,null=True,blank=True)

class AppUser(AbstractBaseUser, PermissionsMixin):
    user_id = models.AutoField(primary_key=True)
    email = models.EmailField(max_length=50, unique=True)
    username = models.CharField(max_length=50)
    role = models.CharField(max_length=50, blank=True, default='Teacher')
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    groups = models.ManyToManyField(Group, related_name='app_users', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='app_users', blank=True)

    objects = AppUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'

    def get_short_name(self):
        return self.username

    def __str__(self):
        return self.username


class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(null=True,blank=True)
    order = models.IntegerField()
    image_link = models.URLField(null=True,blank=True)
    video_link = models.URLField(null=True,blank=True)
    instructorId = models.IntegerField(null=True,blank=True)
    num_lessons = models.IntegerField(default=0)
    
    def get_lessons(self):
        return Lesson.objects.filter(module=self).order_by('order')
    
    def save(self, *args, **kwargs):
        super(Module, self).save(*args, **kwargs)
        course = self.course
        course.num_modules = Module.objects.filter(course=course).count()
        course.save()
        

    def __str__(self):
        return self.title
    
class Lesson(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    order = models.IntegerField()
    image_link = models.URLField(null=True,blank=True)
    video_link = models.URLField(null=True,blank=True)
    instructorId = models.IntegerField(null=True,blank=True)
    
    def save(self, *args, **kwargs):
        super(Lesson, self).save(*args, **kwargs)
        course = self.course
        course.num_lessons = Lesson.objects.filter(module__course=course).count()
        course.save()
        
        module = self.module
        module.num_lessons = Lesson.objects.filter(module=module).count()
        module.save()

    # def save(self, *args, **kwargs):
    #     super(Lesson, self).save(*args, **kwargs)
    #     module = self.module
    #     module.num_lessons = Lesson.objects.filter(module=module).count()
    #     module.save()
        
    def __str__(self):
        return self.title
    
class Enrollment(models.Model):
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)

class CompletedLesson(models.Model):
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    completed_at = models.DateTimeField(auto_now_add=True)
    course= models.ForeignKey(Course, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    
class UserCart(models.Model):
    user=models.ForeignKey(AppUser, on_delete=models.CASCADE)
    course=models.ForeignKey(Course, on_delete=models.CASCADE)
    
    

# # Basic Information
    # first_name = models.CharField(max_length=50, null=True, blank=True)
    # last_name = models.CharField(max_length=50, null=True, blank=True)
    # date_of_birth = models.DateField(null=True, blank=True)
    # gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], null=True, blank=True)
    # profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)

    # # Authentication and Authorization
    # role = models.CharField(max_length=20, null=True, blank=True)
    # password = models.CharField(max_length=128)  # This should be hashed

    # # Contact Information
    # address = models.TextField(null=True, blank=True)
    # phone_number = models.CharField(max_length=15, null=True, blank=True)

    # # Educational Information
    # student_id = models.CharField(max_length=20, null=True, blank=True)
    # institution = models.CharField(max_length=100, null=True, blank=True)
    # grade_class = models.CharField(max_length=20, null=True, blank=True)
    # subject_department = models.CharField(max_length=50, null=True, blank=True)

    # # Learning Progress
    # enrolled_courses = models.ManyToManyField(Course, related_name='enrolled_users', blank=True)
    # completed_courses = models.ManyToManyField(Course, related_name='completed_users', blank=True)