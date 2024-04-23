from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from scheduler.models import UserTable, CourseTable, LabTable


class AdminAssignmentPage:
    def __init__(self):
        pass

    def displayAdminAssignment(self):
        # Display admin assignment details
        pass

    def createCourse(self, courseName, instructorId):
        # Create a new course
        if CourseTable.objects.filter(courseName=courseName).exists():
            raise ValueError("Course already exists")
        elif courseName == "":
            raise ValueError("Invalid course name")
        elif not UserTable.objects.filter(id=instructorId).exists():
            raise ValueError("Invalid instructor")
        else:
            newCourse = CourseTable(courseName=courseName, instructorId=UserTable.objects.get(id=instructorId))
            newCourse.save()
            return True

    def createAccount(self, username, email, password):
        # Create a new account
        if len(password) < 8:
            return False
        if User.objects.filter(email=email).exists():
            return False
        else:
            newAccount = User(username=username, email=email, password=password)
            newUser = UserTable(email=email)
            newAccount.save()
            newUser.save()
            return True


    def editAccount(self, user_id, email, phone, address, role):
        # Edit an existing user account
        pass

    @staticmethod
    def deleteAccount(username, email):
        try:
            # Get the user account based on username and email
            user = UserTable.objects.get(email=email)
            account = User.objects.get(username=username)

            # Delete children
            if user.userType == "TA":
                LabTable.objects.filter(taId=user.id).delete()
            elif user.userType == "Instructor":
                CourseTable.objects.filter(instructorId=user.id).delete()

            # Finally delete user...
            user.delete()

            # Delete the account
            account.delete()
            return True
        except ObjectDoesNotExist:
            return False

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