from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from pip._vendor.requests.models import Response

import adminAssignmentPage
from .models import CourseTable, UserTable, LabTable, AccountTable


def home(request):
    return render(request, 'home.html')


def courseManagement(request):
    courses = CourseTable.objects.all()
    TAs = UserTable.objects.filter(userType="TA")
    instructors = UserTable.objects.filter(userType="Instructor")
    labs = LabTable.objects.all()
    return render(request, 'courseManagement.html',
                  {'courses': courses, 'TAs': TAs, 'instructors': instructors, 'labs': labs})


def createCourse(request):
    if request.method == 'POST':
        courseName = request.POST.get('courseName')
        courseTime = request.POST.get('courseTime')
        courseDays = request.POST.get('courseDays')

        # Create a new CourseTable object
        newCourse = CourseTable(courseName=courseName)
        newCourse.save()

        return courseManagement(request)
        # return HttpResponse('Course created successfully')


def createAccount(request):
    # Stub method, complete later
    return render(request, 'createAccount.html')


class AdminAccManagement(View):
    @staticmethod
    def get(request):
        return render(request, 'adminAccManagement.html')

    @staticmethod
    def post(request):
        if request.method == 'POST':
            if 'deleteAccBtn' in request.POST:
                username = request.POST.get('deleteAccountName')
                email = request.POST.get('deleteAccountEmail')
                adminPage = adminAssignmentPage.AdminAssignmentPage()
                accDeleted = adminPage.deleteAccount(username=username, email=email)
                if accDeleted:
                    return render(request, 'adminAccManagement.html', {'message': "Account deleted successfully"})
                else:
                    return render(request, 'adminAccManagement.html', {'message': "Failed to delete account"})
