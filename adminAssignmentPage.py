from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

from scheduler.models import UserTable, CourseTable, LabTable, SectionTable, UserCourseJoinTable
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
    def createLabSection(courseId, sectionNumber):
        if sectionNumber == "":
            raise ValueError("Invalid section number")
        try:
            # Check if the course exists
            course = CourseTable.objects.get(id=courseId)
            # Check if the section already exists for the given course
            if SectionTable.objects.get(userCourseJoinId=course, name=sectionNumber).exists():
                raise ValueError("Lab section already exists for this course")
            # Create the lab section
            lab_section = SectionTable.objects.create(name=sectionName, userCourseJoinId=course)
            # Create the lab
            LabTable.objects.create(sectionNumber=sectionNumber, sectionId=lab_section)
            return True, "Lab section created successfully"
        except CourseTable.DoesNotExist:
            return False, "Course does not exist"
        except SectionTable.DoesNotExist:
            return False, "Section does not exist"

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
        try:
            # Fetch the course and TA from the database
            course = CourseTable.objects.get(pk=course_id)
            ta = UserTable.objects.get(pk=user_id, userType='TA')

            # Using update_or_create to prevent duplicate assignments and handle the operation atomically
            assignment, created = UserCourseJoinTable.objects.update_or_create(
                courseId=course,
                userId=ta,
            )

            if created:
                return True, "TA successfully assigned to course."
            else:
                return False, "TA assignment updated but already existed."

        except CourseTable.DoesNotExist:
            return False, "Course not found."
        except UserTable.DoesNotExist:
            return False, "TA not found or not eligible."
        except MultipleObjectsReturned:
            return False, "Multiple entries found where only one expected. Data integrity error."
        except Exception as e:
            return False, f"An error occurred: {str(e)}"

    def assignTAToLab(self, lab_id, user_id):
        # Assign a TA to a lab
        pass

    @staticmethod
    def getRole(email):
        try:
            return UserTable.objects.get(email=email).userType
        except ObjectDoesNotExist:
            return None

    @staticmethod
    def createSection(sectionName, joinTableId):
        # Create a new course section
        try:
            joinTable = UserCourseJoinTable.objects.get(id=joinTableId)
            existingCourseSection = SectionTable.objects.filter(userCourseJoinId__courseId=joinTable.courseId,
                                                                name=sectionName).first()
            if existingCourseSection:
                raise ValueError("Section already exists")
            elif sectionName == "":
                raise ValueError("Invalid course name")
            SectionTable.objects.create(name=sectionName, userCourseJoinId=joinTable)
            return "Section created successfully"
        except ObjectDoesNotExist:
            return "Failed to create section"
