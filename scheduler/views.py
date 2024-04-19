from django.shortcuts import render
from .models import CourseTable, UserTable, LabTable

def home(request):
    return render(request, 'home.html')

def courseManagement(request):
    courses = CourseTable.objects.all()
    TAs = UserTable.objects.filter(userType="TA")
    instructors = UserTable.objects.filter(userType="Instructor")
    labs = LabTable.objects.all()
    return render(request, 'courseManagement.html',{'courses':courses,'TAs':TAs,'instructors': instructors, 'labs':labs})

def createCourse(request):
    if request.method == 'POST':
        courseName = request.POST.get('courseName')
        courseTime = request.POST.get('courseTime')
        courseDays = request.POST.get('courseDays')

        # Create a new CourseTable object
        newCourse = CourseTable(courseName=courseName)
        newCourse.save()

        return courseManagement(request)
        #return HttpResponse('Course created successfully')


def createAccount(request):
    #Stub method, complete later
    return render(request, 'createAccount.html')
