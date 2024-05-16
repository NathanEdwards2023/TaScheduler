import re

from django.contrib.auth.models import User

from scheduler.models import UserTable


class ProfilePage:
    def __init__(self):
        pass

    def displayAdminAssignment(self):
        # Display admin assignment details
        pass

    def editProfile(self, old_email, first_name, last_name, email, phone, address, skills):
        try:
            user = UserTable.objects.get(email=old_email)
            pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

            if not re.match(pattern, email):
                raise ValueError("Invalid email format")

            if email != old_email:
                # Check if the new email is already in use
                if UserTable.objects.filter(email=email).exclude(email=old_email).exists():
                    raise ValueError("New email is already in use by another user.")

            # Update user attributes
            user.firstName = first_name
            user.lastName = last_name
            user.email = email
            user.phone = phone
            user.address = address
            user.skills = skills
            user.save()

            # Also update the associated User model email if changed
            account = User.objects.get(email=old_email)
            account.email = email
            account.save()

            return user
        except UserTable.DoesNotExist:
            raise ValueError("User account does not exist.")
        except Exception as e:
            raise ValueError(str(e))
