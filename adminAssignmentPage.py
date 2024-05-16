from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

from scheduler.models import UserTable, CourseTable, LabTable, SectionTable, UserCourseJoinTable, UserLabJoinTable, \
    UserSectionJoinTable
import re


class AdminAssignmentPage:
    def __init__(self):
        pass

    def displayAdminAssignment(self):
        # Display admin assignment details
        pass

    @staticmethod
    def createCourse(courseName, instructorId):
        # Create a new course
        if CourseTable.objects.filter(courseName=courseName).exists():
            raise ValueError("Course already exists")
        elif courseName == "":
            raise ValueError("Invalid course name")
        elif instructorId != "" and not UserTable.objects.filter(id=instructorId).exists():
            raise ValueError("Invalid instructor")
        else:
            newCourse = CourseTable(courseName=courseName)
            newCourse.save()
            if instructorId != "":
                instructor = UserTable.objects.get(id=instructorId)
                newJoin = UserCourseJoinTable(userId=instructor, courseId=newCourse)
                newJoin.save()
            return True

    @staticmethod
    def editCourse(course_id, courseName, instructorID, time):
        try:
            course = CourseTable.objects.get(id=course_id)

            if courseName == "":
                raise ValueError("Invalid course name")

            if instructorID:
                instructor = UserTable.objects.get(id=instructorID)
                course.instructorId = instructor.id

            if courseName:
                course.courseName = courseName

            if time:
                course.time = time

            course.save()
            return True

        except CourseTable.DoesNotExist:
            raise ValueError("Course does not exist")

    @staticmethod
    def deleteCourse(courseId):
        try:
            course = CourseTable.objects.get(id=courseId)
            course.delete()
            return True
        except CourseTable.objects.get(id=courseId).DoesNotExist:
            # Handle the case where the course does not exist
            return ValueError("Course does not exist")

    @staticmethod
    def createLabSection(courseId, sectionNumber):
        if sectionNumber == "":
            raise ValueError("Invalid section number")
        try:
            course = CourseTable.objects.get(id=courseId)
            # Check if the section already exists for the given course
            if SectionTable.objects.filter(courseId=course, name=sectionNumber).exists():
                lab_section = SectionTable.objects.get(courseId=course, name=sectionNumber)
            else:
                # Create the lab section
                lab_section = SectionTable.objects.create(name=sectionNumber, courseId=course)
                lab_section.save()

            if LabTable.objects.filter(sectionNumber=sectionNumber, section=lab_section).exists():
                raise ValueError("Lab section already exists")
            else:
                # Create the lab
                lab = LabTable.objects.create(sectionNumber=sectionNumber, section=lab_section)
                lab.save()
            return True
        except CourseTable.DoesNotExist:
            raise ValueError("Course does not exist")
        except SectionTable.DoesNotExist:
            raise ValueError("Section does not exist")

    @staticmethod
    def createAccount(username, email, password):
        pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

        if username == '' or email == '' or password == '':
            raise ValueError("All fields need to be filled out")

        if not re.match(pattern, email):
            raise ValueError("Invalid email format")

        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")

        try:
            existing_email = User.objects.get(email=email)
            raise ValueError("User already exists")
        except User.DoesNotExist:
            pass

        newAccount = User.objects.create_user(username=username, email=email, password=password)
        newUser = UserTable(email=email)
        newAccount.save()
        newUser.save()
        return True

    def editAccount(self, email, newEmail, phone, address, role):
        try:
            user = UserTable.objects.get(email=email)

            user.email = newEmail
            user.phone = phone
            user.address = address
            user.userType = role
            user.save()

            account = User.objects.get(email=email)
            account.email = newEmail
            account.save()

            return user
        except UserTable.DoesNotExist:
            raise ValueError("User account does not exist.")
        except Exception as e:
            raise ValueError(str(e))
