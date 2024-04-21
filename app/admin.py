# admin.py

from django.contrib import admin
from .models import *

admin.site.register(Course)
admin.site.register(AppUser)
admin.site.register(Category)
admin.site.register(Module)
admin.site.register(Lesson)
admin.site.register(Enrollment)
admin.site.register(CompletedLesson)
admin.site.register(UserCart)


