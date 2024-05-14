from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from pip._vendor.requests.models import Response
from django.contrib.auth.decorators import login_required

import adminAssignmentPage
from .models import CourseTable, UserTable, LabTable


@login_required(login_url='login')
def home(request):
    return render(request, 'home.html')


@login_required(login_url='login')
def courseManagement(request):
    courses = CourseTable.objects.all()
    TAs = UserTable.objects.filter(userType="TA")
    instructors = UserTable.objects.filter(userType="Instructor")
    labs = LabTable.objects.all()

    if request.method == 'GET':
        user = request.user
        accRole = UserTable.objects.get(email=user.email).userType
        if user.is_authenticated and accRole == 'admin':
            return render(request, 'courseManagement.html',
                          {'courses': courses, 'TAs': TAs, 'instructors': instructors, 'labs': labs})
        else:
            # Redirect non-admin users to another page (e.g., home page)
            return redirect('home')

    else:
        if request.method == 'POST' and 'createCourseBtn' in request.POST:
            courseName = request.POST.get('courseName')
            courseTime = request.POST.get('courseTime')
            courseDays = request.POST.get('courseDays')
            instructor = request.POST.get('instructorSelect')

            # Create a new CourseTable object
            admin_page = adminAssignmentPage.AdminAssignmentPage()
            try:
                admin_page.createCourse(courseName, instructor)
                return render(request, 'courseManagement.html',
                              {'courses': courses, 'TAs': TAs, 'instructors': instructors, 'labs': labs,
                               'messages': "Course successfully created"})
            except ValueError as msg:
                return render(request, 'courseManagement.html',
                              {'courses': courses, 'TAs': TAs, 'instructors': instructors, 'labs': labs,
                               'messages': msg})
        if request.method == 'POST' and 'editCourseBtn' in request.POST:
            courseID = request.POST.get("editCourseSelect")
            courseName = request.POST.get('editName')
            courseTime = request.POST.get('editTime')
            instructor = request.POST.get('editInstructorSelect')

            # Create a new CourseTable object
            admin_page = adminAssignmentPage.AdminAssignmentPage()
            try:
                admin_page.editCourse(courseID, courseName, instructor, courseTime)
                return render(request, 'courseManagement.html',
                              {'courses': courses, 'TAs': TAs, 'instructors': instructors, 'labs': labs,
                               'messages': "Course successfully created"})
            except ValueError as msg:
                return render(request, 'courseManagement.html',
                              {'courses': courses, 'TAs': TAs, 'instructors': instructors, 'labs': labs,
                               'messages': msg})
        return redirect('courseManagement')
    return render(request, 'courseManagement.html')


class AdminAccManagement(View):
    @staticmethod
    @login_required(login_url='login')
    def get(request):
        users = User.objects.all
        user = request.user
        accRole = UserTable.objects.get(email=request.user.email).userType
        if user.is_authenticated and accRole == 'admin':
            return render(request, 'adminAccManagement.html',
                          {'users': users})
        else:

            # Redirect non-admin users to another page (e.g., home page)
            return redirect('home')

    @staticmethod
    def post(request):
        users = User.objects.all
        if request.method == 'POST':
            if 'deleteAccBtn' in request.POST:
                #             instructor = request.POST.get('instructorSelect')
                username = request.POST.get('deleteAccountName')
                email = request.POST.get('deleteAccountEmail')
                adminPage = adminAssignmentPage.AdminAssignmentPage()
                accDeleted = adminPage.deleteAccount(usernameID=username, emailID=email)
                return render(request, 'adminAccManagement.html', {'users': users, 'message': accDeleted})

            if 'createAccBtn' in request.POST:
                username = request.POST.get('createAccountName')
                email = request.POST.get('createAccountEmail')
                password = request.POST.get('createAccountPassword')
                adminPage = adminAssignmentPage.AdminAssignmentPage()
                try:
                    adminPage.createAccount(username=username, email=email, password=password)
                    return render(request, 'adminAccManagement.html', {'messageCreateAcc': "Account created"})
                except ValueError as msg:
                    return render(request, 'adminAccManagement.html', {'messageCreateAcc': msg})

            if 'editAccBtn' in request.POST:
                user_id = request.POST.get('user_id')
                email = request.POST.get('email')
                phone = request.POST.get('phone')
                address = request.POST.get('address')
                role = request.POST.get('role')
                adminPage = adminAssignmentPage.AdminAssignmentPage()
                try:
                    adminPage.editAccount(user_id, email, phone, address, role)
                    return render(request, 'adminAccManagement.html', {'messageEditAcc': "Account edited"})
                except ValueError as msg:
                    return render(request, 'adminAccManagement.html', {'messageCreateAcc': msg})
        return render(request, 'adminAccManagement.html', {'users': User.objects.all()})
