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
                print("Lab section:")
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
            ta = UserTable.objects.get(pk=user_id, userType='ta')

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
        try:
            lab = LabTable.objects.get(pk=lab_id)
            ta = UserTable.objects.get(pk=user_id, userType='ta')
            section = SectionTable.objects.get(id=lab.section_id)

            if not section:
                return False, "Section not found. Ensure the lab is linked to a section."

            # Proceed with assignments
            lab_assignment, lab_created = UserLabJoinTable.objects.update_or_create(
                labId=lab,
                userId=ta,
                defaults={'labId': lab, 'userId': ta}
            )

            section_assignment, section_created = UserSectionJoinTable.objects.update_or_create(
                sectionId=section,
                userId=ta,
                defaults={'sectionId': section, 'userId': ta}
            )

            if lab_created or section_created:
                return True, "TA successfully assigned to lab and corresponding section."
            return False, "TA assignment to lab and section already existed."

        except LabTable.DoesNotExist:
            return False, "Lab not found."
        except UserTable.DoesNotExist:
            return False, "TA not found or not eligible."
        except SectionTable.DoesNotExist:
            return False, "Section not found linked to the lab."
        except Exception as e:
            return False, f"An unexpected error occurred: {str(e)}"


    @staticmethod
    def getRole(email):
        try:
            return UserTable.objects.get(email=email).userType
        except ObjectDoesNotExist:
            return None

    @staticmethod
    def createSection(sectionName, courseId, time):
        # Create a new course section
        try:
            print("TEST made it")
            course = CourseTable.objects.filter(id=courseId).first()
            existingCourseSection = SectionTable.objects.filter(name=sectionName, courseId=course).exists()

            if existingCourseSection:
                raise ValueError("Section already exists")
            elif sectionName == "":
                raise ValueError("Invalid course name")
            print(sectionName, course, time)
            SectionTable.objects.create(name=sectionName, courseId=course, time=time)
            return "Section created successfully"
        except ObjectDoesNotExist:
            return "Failed to create section"
