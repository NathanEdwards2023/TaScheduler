from django.core.exceptions import ObjectDoesNotExist

from scheduler.models import CourseTable, UserTable, UserCourseJoinTable


class AdminCourseManagementPage:
    def __init__(self):
        pass

    @staticmethod
    def assignInstructorToCourse(courseId, userId):
        try:
            courseExist = CourseTable.objects.filter(id=courseId).exists()
            if courseExist:
                course = CourseTable.objects.filter(id=courseId).first()
            else:
                raise ValueError("Course does not exist")

            userExist = UserTable.objects.filter(id=userId).exists()
            if userExist:
                user = UserTable.objects.filter(id=userId).first()
            else:
                raise ValueError("User does not exist")
            if user.userType != "instructor":
                raise ValueError("User is not an instructor")

            existingUserCourse = UserCourseJoinTable.objects.filter(courseId=course, userId=user).exists()
            if existingUserCourse:
                raise ValueError("Course assignment already exists")
            UserCourseJoinTable.objects.create(courseId=course, userId=user)
            return "Section created successfully"
        except ObjectDoesNotExist:
            return "Failed to create section"
