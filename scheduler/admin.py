from django.contrib import admin
from .models import AccountTable, UserTable, CourseTable, LabTable

# Register your models here.
admin.site.register(AccountTable)
admin.site.register(UserTable)
admin.site.register(CourseTable)
admin.site.register(LabTable)
