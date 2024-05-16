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
