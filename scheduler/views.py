from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from pip._vendor.requests.models import Response
from django.contrib.auth.decorators import login_required
from django.contrib import messages

import adminAssignmentPage, adminCourseManagement, adminSectionManagement
from .models import CourseTable, UserTable, LabTable, UserCourseJoinTable, UserLabJoinTable, UserSectionJoinTable, \
    SectionTable


@login_required(login_url='login')
def home(request):
    user = request.user
    userType = UserTable.objects.get(email=user.email).userType
    return render(request, 'home.html', {'userType': userType})


@login_required(login_url='login')
def profile(request):
    user = request.user
    user_data = UserTable.objects.get(email=user.email)
    return render(request, 'profile.html', {'user_data': user_data})


@login_required(login_url='login')
def courseManagement(request):
    courses = CourseTable.objects.all()
    TAs = UserTable.objects.filter(userType="ta")
    instructors = UserTable.objects.filter(userType="instructor")
    labs = LabTable.objects.all()
    joinEntries = UserCourseJoinTable.objects.all()

    if request.method == 'GET':
        user = request.user
        accRole = UserTable.objects.get(email=user.email).userType
        if user.is_authenticated and accRole == 'admin':
            return render(request, 'courseManagement.html',
                          {'courses': courses, 'TAs': TAs, 'instructors': instructors,
                           'joinEntries': joinEntries, 'labs': labs})
        else:
            # Redirect non-admin users to another page (e.g., home page)
            return redirect('home')

    else:
        if request.method == 'POST':
            admin_page = adminAssignmentPage.AdminAssignmentPage()
            adminCMPage = adminCourseManagement.AdminCourseManagementPage()
            adminSMPage = adminSectionManagement.AdminSectionManagementPage()

            if 'createCourseBtn' in request.POST:
                courseName = request.POST.get('courseName')
                instructor = request.POST.get('instructorSelect')
                # Create a new CourseTable object
                try:
                    adminCMPage.createCourse(courseName, instructor)
                    return render(request, 'courseManagement.html',
                                  {'courses': courses, 'TAs': TAs, 'instructors': instructors, 'labs': labs,
                                   'joinEntries': joinEntries, 'createMessages': "Course successfully created"})
                except ValueError as msg:
                    return render(request, 'courseManagement.html',
                                  {'courses': courses, 'TAs': TAs, 'instructors': instructors, 'labs': labs,
                                   'joinEntries': joinEntries, 'createMessages': msg})

            if 'createSectionBtn' in request.POST:
                sectionName = request.POST.get('courseSection')
                courseTable = request.POST.get('courseSectionSelect')
                time = request.POST.get('courseSectionTime')

                # Create a new section object
                try:
                    msg = admin_page.createSection(sectionName, courseTable, time)
                    return render(request, 'courseManagement.html',
                                  {'courses': courses, 'TAs': TAs, 'instructors': instructors, 'labs': labs,
                                   'joinEntries': joinEntries, 'createMessages': msg})
                except ValueError as msg:
                    return render(request, 'courseManagement.html',
                                  {'courses': courses, 'TAs': TAs, 'instructors': instructors, 'labs': labs,
                                   'joinEntries': joinEntries, 'createMessages': msg})

            if 'assignBtn' in request.POST:
                courseId = request.POST.get('courseSelect')
                insUserid = request.POST.get('instructorSelect')

                # Create a new section object
                try:
                    msg = admin_page.assignInstructorToCourse(courseId, insUserid)
                    return render(request, 'courseManagement.html',
                                  {'courses': courses, 'TAs': TAs, 'instructors': instructors, 'labs': labs,
                                   'joinEntries': joinEntries, 'assignCourseMsg': msg})
                except ValueError as msg:
                    return render(request, 'courseManagement.html',
                                  {'courses': courses, 'TAs': TAs, 'instructors': instructors, 'labs': labs,
                                   'joinEntries': joinEntries, 'assignCourseMsg': msg})

            if 'assignTAToCourseBtn' in request.POST:
                course_id = request.POST.get('courseId')
                user_id = request.POST.get('userId')  # Note the changed parameter name
                admin_page = adminAssignmentPage.AdminAssignmentPage()
                success, message = admin_page.assignTAToCourse(course_id, user_id)

                if success:
                    messages.success(request, message)
                else:
                    messages.error(request, message)

            if 'deleteBtn' in request.POST:
                courseId = request.POST.get('sectionSelect')
                try:
                    adminCMPage.deleteCourse(courseId)
                    courses = CourseTable.objects.all()
                    labs = LabTable.objects.all()
                    joinEntries = UserCourseJoinTable.objects.all()
                    return render(request, 'courseManagement.html',
                                  {'courses': courses, 'TAs': TAs, 'instructors': instructors, 'labs': labs,
                                   'joinEntries': joinEntries, 'deleteMessages': "Course successfully deleted"})
                except ValueError as msg:
                    return render(request, 'courseManagement.html',
                                  {'courses': courses, 'TAs': TAs, 'instructors': instructors, 'labs': labs,
                                   'joinEntries': joinEntries, 'deleteMessages': msg})

            if 'assignTAToLabBtn' in request.POST:
                lab_id = request.POST.get('labId')
                user_id = request.POST.get('userId')
                admin_page = adminAssignmentPage.AdminAssignmentPage()

                success, message = admin_page.assignTAToLab(lab_id, user_id)
                if success:
                    messages.success(request, message, extra_tags='lab_success')
                else:
                    messages.error(request, message, extra_tags='lab_error')
                return redirect('courseManagement')

            if 'createLabBtn' in request.POST:
                labSection = request.POST.get('labSection')
                courseSelect = request.POST.get('courseSelect')

                try:
                    adminSMPage.createLabSection(courseSelect, labSection)
                    return render(request, 'courseManagement.html',
                                  {'courses': courses, 'TAs': TAs, 'instructors': instructors, 'labs': labs,
                                   'joinEntries': joinEntries, 'createMessages': "Lab successfully created"})

                except ValueError as msg:
                    return render(request, 'courseManagement.html',
                                  {'courses': courses, 'TAs': TAs, 'instructors': instructors, 'labs': labs,
                                   'joinEntries': joinEntries, 'createMessages': msg})

        return redirect('courseManagement')


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
                    return render(request, 'adminAccManagement.html',
                                  {'users': users, 'messageCreateAcc': "Account created"})
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
        return render(request, 'adminAccManagement.html', {'users': users})


class InsCourseManagement(View):
    @staticmethod
    @login_required(login_url='login')
    def get(request):
        TAs = UserTable.objects.filter(userType="ta")
        user = request.user
        userTable = UserTable.objects.get(email=request.user.email)
        userCourses = UserCourseJoinTable.objects.filter(userId=userTable)
        userCourseId = [courseId.courseId for courseId in userCourses]
        insSimilarCourses = UserCourseJoinTable.objects.filter(courseId__in=userCourseId, userId__userType="instructor")

        if user.is_authenticated and userTable.userType == 'instructor':
            return render(request, 'insCourseManagement.html',
                          {'TAs': TAs, 'userCourseId': userCourseId, insSimilarCourses: 'insSimilarCourses'})
        else:

            # Redirect non-admin users to another page (e.g., home page)
            return redirect('home')

    @staticmethod
    def post(request):
        TAs = UserTable.objects.filter(userType="ta")
        userTable = UserTable.objects.get(email=request.user.email)
        userCourses = UserCourseJoinTable.objects.filter(userId=userTable)
        userCourseId = [courseId.courseId for courseId in userCourses]
        insSimilarCourses = UserCourseJoinTable.objects.filter(courseId__in=userCourseId, userId__userType="instructor")

        if request.method == 'POST':
            if 'courseBtn' in request.POST:
                courseId = request.POST.get('courseSelect')
                try:
                    course = CourseTable.objects.get(id=courseId)
                    otherInstructors = UserCourseJoinTable.objects.filter(courseId=course,
                                                                          userId__userType='instructor')
                    sections = SectionTable.objects.filter(courseId=course)

                    return render(request, 'insCourseManagement.html',
                                  {'TAs': TAs, 'userCourseId': userCourseId, insSimilarCourses: 'insSimilarCourses',
                                   'instructors': otherInstructors, 'sections': sections,
                                   'createMessages': "Course Selected"})
                except ValueError as msg:
                    return render(request, 'insCourseManagement.html',
                                  {'TAs': TAs, 'userCourseId': userCourseId, insSimilarCourses: 'insSimilarCourses',
                                   'createMessages': msg})
            elif 'insToSectionBtn' in request.POST:
                instructorId = request.POST.get('instructorSelect')
                sectionId = request.POST.get('sectionSelect')
                try:
                    adminPage = adminAssignmentPage.AdminAssignmentPage()
                    msg = adminPage.assignInsToSection(sectionId, instructorId)
                    return render(request, 'insCourseManagement.html',
                                  {'TAs': TAs, 'userCourseId': userCourseId, 'createMessages': msg})
                except ValueError as msg:
                    return render(request, 'insCourseManagement.html', {'TAs': TAs, 'userCourseId': userCourseId,
                                                                        'createMessages': msg,
                                                                        insSimilarCourses: 'insSimilarCourses'})

        return render(request, 'insCourseManagement.html', {'TAs': TAs, 'userCourseId': userCourseId})
