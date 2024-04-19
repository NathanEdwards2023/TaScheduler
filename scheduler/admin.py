from django.contrib import admin
from .models import UserTable, AccountTable, CourseTable, LabTable

# Register your models here.
admin.site.register(UserTable)
admin.site.register(AccountTable)
admin.site.register(CourseTable)
admin.site.register(LabTable)
