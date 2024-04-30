from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from scheduler.models import UserTable, CourseTable, LabTable, UserCourseJoinTable, SectionTable
import re

class AdminAssignmentPage:
    def __init__(self):
        pass

    def displayAdminAssignment(self):
        # Display admin assignment details
        pass

    def editCourse(self, course_id, courseName, instructorID, time):
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
    def deleteCourse(courseId):
        if CourseTable.objects.get(id=courseId).DoesNotExist:
            return ValueError("Course does not exist")
        try:
            course = CourseTable.objects.get(id=courseId)
            ucjt = UserCourseJoinTable.objects.filter(courseId=courseId)
            for ucj in ucjt:
                sect = SectionTable.objects.filter(userCourseJoinId=ucj)
                for sec in sect:
                    labt = LabTable.objects.filter(sectionId=sec)
                    for lab in labt:
                        lab.delete()
                    sec.delete()
                ucj.delete()
            course.delete()
            return True
        except CourseTable.objects.get(id=courseId).DoesNotExist:
            # Handle the case where the course does not exist
            # You can render an error message or redirect to an error page
            return ValueError("Course does not exist")

    @staticmethod
    def createLabSection(labId, courseId):
        pass

    @staticmethod
    def createAccount(username, email, password):
        pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

        if username == "" or email == "" or password == "":
            raise ValueError("All fields need to be filled out")

        if not re.match(pattern, email):
            raise ValueError("Invalid email format")

        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")

        if User.objects.filter(email=email).exists():
            raise ValueError("User with this email already exists")

        newAccount = User.objects.create_user(username=username, email=email, password=password)
        newUser = UserTable(email=email)
        newAccount.save()
        newUser.save()
        return True


    def editAccount(self, user_id, email, phone, address, role):
        # Edit an existing user account
        pass

    # needs to be static
    @staticmethod
    def deleteAccount(usernameID, emailID):
        try:
            # Get the user account based on username and email
            account = User.objects.get(id=usernameID)
            user = UserTable.objects.filter(email=account.email).first()
            if (account.email != user.email) | (usernameID != emailID):
                return "username/email match error"

            # Delete children
            if user.userType == "ta":
                LabTable.objects.filter(taId=user.id).delete()
            elif user.userType == "instructor":
                CourseTable.objects.filter(instructorId=user.id).delete()

            # Finally delete user...
            user.delete()
            # Delete the account
            account.delete()
            return "Account deleted successfully"
        except ObjectDoesNotExist:
            return "Failed to delete account"

    def assignInstructorToCourse(self, course_id, user_id):
        # Assign an instructor to a course
        pass

    def assignTAToCourse(self, course_id, user_id):
        # Assign a TA to a course
        pass

    def assignTAToLab(self, lab_id, user_id):
        # Assign a TA to a lab
        pass

    def getRole(self, email):
        # get the accs role
        pass