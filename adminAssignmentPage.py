from django.core.exceptions import ObjectDoesNotExist

from scheduler.models import UserTable, AccountTable, CourseTable, LabTable


class AdminAssignmentPage:
    def __init__(self):
        pass

    def displayAdminAssignment(self):
        # Display admin assignment details
        pass

    def createCourse(self, course_name, instructorId):
        # Create a new course
        pass

    def createAccount(self, username, email, password):
        # Create a new user account

        pass

    def editAccount(self, user_id, email, phone, address, role):
        # Edit an existing user account
        pass

    @staticmethod
    def deleteAccount(username, email):
        try:
            # Get the user account based on username and email
            user = UserTable.objects.get(email=email)
            account = AccountTable.objects.get(username=username)

            # Delete children
            if user.userType == "TA":
                LabTable.objects.filter(taId=user.id).delete()
            elif user.userType == "Instructor":
                CourseTable.objects.filter(instructorId=user.id).delete()

            # Delete the account
            account.delete()
            # Finally delete user...
            user.delete()

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