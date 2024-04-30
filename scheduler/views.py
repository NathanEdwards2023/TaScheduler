from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from pip._vendor.requests.models import Response
from django.contrib.auth.decorators import login_required
from django.contrib import messages


import adminAssignmentPage
from .models import CourseTable, UserTable, LabTable, UserCourseJoinTable


@login_required(login_url='login')
def home(request):
    return render(request, 'home.html')


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
            instructorId = request.POST.get('instructorSelect')
            admin_page = adminAssignmentPage.AdminAssignmentPage()
            try:
                admin_page.createCourse(courseName, instructorId)
                return render(request, 'courseManagement.html',
                              {'courses': courses, 'TAs': TAs, 'instructors': instructors, 'labs': labs,
                               'createMessages': "Course successfully created"})
            except ValueError as msg:
                return render(request, 'courseManagement.html',
                              {'courses': courses, 'TAs': TAs, 'instructors': instructors, 'labs': labs,
                               'createMessages': msg})
        elif request.method == 'POST' and 'deleteCourseBtn' in request.POST:
            courseId = request.POST.get('sectionSelect')
            admin_page = adminAssignmentPage.AdminAssignmentPage()
            try:
                admin_page.deleteCourse(courseId)
                return render(request, 'courseManagement.html',
                              {'courses': courses, 'TAs': TAs, 'instructors': instructors, 'labs': labs,
                               'deleteMessages': "Course successfully deleted"})
            except ValueError as msg:
                return render(request, 'courseManagement.html',
                              {'courses': courses, 'TAs': TAs, 'instructors': instructors, 'labs': labs,
                               'deleteMessages': msg})
        elif 'assignTAToCourseBtn' in request.POST:
            course_id = request.POST.get('courseId')
            user_id = request.POST.get('userId')  # Note the changed parameter name
            admin_page = adminAssignmentPage.AdminAssignmentPage()
            success, message = admin_page.assignTAToCourse(course_id, user_id)

            if success:
                messages.success(request, message)
            else:
                messages.error(request, message)

            return redirect('courseManagement')

            return render(request, 'courseManagement.html', {
                'courses': courses,
                'TAs': TAs,
                'instructors': instructors,
                'labs': labs
            })


def createAccount(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        adminPage = adminAssignmentPage.AdminAssignmentPage()
        accountCreated = adminPage.createAccount(username=username, email=email, password=password)
        if accountCreated:
            return render(request, 'createAccount.html', {'username': username, 'email': email, 'password': password,
                                                          'messages': "Account created successfully"})
        else:
            return render(request, 'createAccount.html', {'username': username, 'email': email, 'password': password,
                                                          'messages': "Account failed to be created"})

    return render(request, 'createAccount.html')


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
