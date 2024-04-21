from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Category, Course

class CategoryTestCase(TestCase):
    def setUp(self):
        Category.objects.create(title='Test Category')

    def test_category_creation(self):
        category = Category.objects.get(title='Test Category')
        self.assertEqual(category.title, 'Test Category')

class CourseAPITestCase(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(title='Test Category')
        self.course = Course.objects.create(
            title='Test Course',
            category=self.category,
            description='Test Description'
        )

    def test_get_courses_list(self):
        url = reverse('get-courses')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_course_detail(self):
        url = reverse('course-detail', kwargs={'pk': self.course.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Add more test cases for other API endpoints as needed

    # def test_enroll_course(self):
    #     url = reverse('enroll-course', kwargs={'course_id': self.course.pk})
    #     response = self.client.post(url)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
