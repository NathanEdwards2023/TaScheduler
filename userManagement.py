from django.core.exceptions import ObjectDoesNotExist

from scheduler.models import UserTable


class UserManagementPage:
    def __init__(self):
        pass

    @staticmethod
    def getRole(email):
        try:
            return UserTable.objects.get(email=email).userType
        except ObjectDoesNotExist:
            return None
