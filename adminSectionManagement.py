from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned


from scheduler.models import UserTable, CourseTable, LabTable, SectionTable, UserCourseJoinTable, UserLabJoinTable, \
    UserSectionJoinTable
import re


class AdminSectionManagementPage:
    def __init__(self):
        pass
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
