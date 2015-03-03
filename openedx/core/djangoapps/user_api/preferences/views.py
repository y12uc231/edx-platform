"""
NOTE: this API is WIP and has not yet been approved. Do not use this API without talking to Christina or Andy.

For more information, see:
https://openedx.atlassian.net/wiki/display/TNL/User+API
"""
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
import datetime
from pytz import UTC

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import OAuth2Authentication, SessionAuthentication
from rest_framework import permissions
from rest_framework import parsers

from ..models import UserPreference
from ..serializers import UserSerializer
from student.views import do_email_change_request
from openedx.core.djangoapps.user_api.accounts import NAME_MIN_LENGTH
from openedx.core.djangoapps.user_api.accounts.serializers import AccountLegacyProfileSerializer, AccountUserSerializer
from openedx.core.lib.api.permissions import IsUserInUrlOrStaff
from openedx.core.lib.api.parsers import MergePatchParser
from openedx.core.djangoapps.user_api.api.account import AccountUserNotFound, AccountUpdateError


class PreferencesView(APIView):
    """
        **Use Cases**

            Get or update the user's preference information. Updates are only supported through merge patch.

        **Example Requests**:

            GET /api/user/v0/preferences/{username}/

            PATCH /api/user/v0/preferences/{username}/ with content_type "application/merge-patch+json"

        **Response Value for GET**

            A dict will be returned with key/value pairs (all of type String).

        **Response for PATCH**

             Returns a 204 status if successful, with no additional content.
             If "application/merge-patch+json" is not the specified content_type, returns a 415 status.

    """
    authentication_classes = (OAuth2Authentication, SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated, IsUserInUrlOrStaff)
    parser_classes = (MergePatchParser,)

    def get(self, request, username):
        """
        GET /api/user/v0/preferences/{username}/
        """
        try:
            existing_user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        user_serializer = UserSerializer(existing_user)
        return Response(user_serializer.data["preferences"])


class PreferencesDetailView(APIView):
    """
        **Use Cases**

            Get, create, update, or delete a specific user preference.

        **Example Requests**:

            GET /api/user/v0/accounts/{username}/{preference_key}

            PUT /api/user/v0/accounts/{username}/{preference_key}

            DELETE /api/user/v0/accounts/{username}/{preference_key}

        **Response Values for PUT**

            TODO

        **Response for PUT**

             TODO

    """
    authentication_classes = (OAuth2Authentication, SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated, IsUserInUrlOrStaff)

    def get(self, request, username, preference_key):
        """
        GET /api/user/v0/preferences/{username}/{preference_key}
        """
        try:
            existing_user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        try:
            preference_value = existing_user.preferences.get(key=preference_key).value
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(preference_value)
