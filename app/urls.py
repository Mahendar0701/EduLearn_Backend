from django.urls import path
from .views import CategoryView, CompletedLessonView, CourseView, EnrollmentView, UserCartDetailView, UserCartView, UserLoginView, UserLogoutView, UserRegisterView, UserView, check_enrollment
from .views import CourseDetailView, ModuleList, ModuleDetailView
from .views import LessonList, LessonDetail
from .views import AllUsersListView
from .views import UserProfileEditView
from .views import EnrolledCoursesListView
from .views import CompletedLessonsInCourseView

urlpatterns = [
    path('categories/', CategoryView.as_view(), name='get-categories'),
    path('courses/', CourseView.as_view(), name='get-courses'),
    path('courses/<int:pk>/', CourseDetailView.as_view(), name='course-detail'),
    path('courses/<int:course_id>/add-to-cart/', UserCartView.as_view(), name='add-to-cart'),  
    path('courses/<int:course_id>/modules/', ModuleList.as_view(), name='module-list'),
    path('courses/<int:course_id>/modules/<int:pk>/', ModuleDetailView.as_view(), name='module-detail'),
    path('courses/<int:course_id>/modules/<int:module_id>/lessons/', LessonList.as_view(), name='lesson-list'),
    path('courses/<int:course_id>/modules/<int:module_id>/lessons/<int:pk>/', LessonDetail.as_view(), name='lesson-detail'),
    
    path('courses/<int:course_id>/modules/<int:module_id>/lessons/<int:lesson_id>/complete/', CompletedLessonView.as_view(), name='complete-lesson'),
    path('courses/<int:course_id>/completed-lessons/', CompletedLessonsInCourseView.as_view(), name='completed-lessons-in-course'),
    path('courses/<int:course_id>/enroll/', EnrollmentView.as_view(), name='enroll-course'),    
    path('user/', UserView.as_view(), name='user-list'),
    path('user/profile/edit/', UserProfileEditView.as_view(), name='user-profile-edit'),
    path('user/cart/', UserCartDetailView.as_view(), name='user-cart-details'),    
    path('user/enrolled-courses/', EnrolledCoursesListView.as_view(), name='enrolled-courses-list'),
    path('all-users/', AllUsersListView.as_view(), name='all-users-list'),    
    path('check-enrollment/<int:course_id>/', check_enrollment, name='check_enrollment'),
    path('signup/', UserRegisterView.as_view(), name='signup'),
    path('signin/', UserLoginView.as_view(), name='signin'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
       
]
