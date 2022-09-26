import hashlib

from django.conf import settings

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from sso.helpers.Log import Log

# https://django-rest-framework-simplejwt.readthedocs.io/en/latest/getting_started.html


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        # We do not want to keep information on logged-in users.
        from django.db import connection
        with connection.cursor() as c:
            c.execute("DELETE FROM auth_user WHERE username = %s and is_superuser != 1", [
                str(self.user)
            ])

        return data

    @classmethod
    def get_token(cls, user):
        if user.username: 
            Log.log("Ask token for user "+user.username + "...")
            # Auth system can be confused from users with and without the @domain part in the login string. If so, set the
            # AUTH_LDAP_USER_QUERY_FIELD parameter in settings.py https://django-auth-ldap.readthedocs.io/en/latest/reference.html
            if not user.username.endswith('@automation.local'):
                Log.log("If this fails maybe you should delete the username "+str(user.username)+" from the auth_user table in the sso db.")

            token = super().get_token(user)

            # Get the groups' list this user belongs to.
            # https://django-auth-ldap.readthedocs.io/en/latest/users.html#direct-attribute-access
            if hasattr(user, 'ldap_user'):
                groups = []
                for g in user.ldap_user.group_dns:
                    # Prevent "tampered" admin group.
                    if g != "automation.local":
                        groups.append(g.lower())
            else:
                groups = []

            # Local superadmin.
            if user.username == "admin@automation.local":
                groups = ["automation.local"]

            # AD superadmin: add automation.local (the superadmin group) to the group list of the user.
            for g in settings.SUPERADMIN_IDENTITY_AD_GROUPS:
                g = g.lower()
                if g in groups:
                    groups.append("automation.local")

            # Add custom claims.
            token['username'] = user.username
            token['uuid'] = str(token['user_id'])+hashlib.md5(str(settings.AUTHENTICATION_BACKENDS).encode('utf-8')).hexdigest()[0:5] # unique userid for this platform (trusting IP authority).
            token['groups'] = groups

            Log.log("Obtained token for user "+str(user.username)+", uuid "+str(token['uuid'])+", groups "+str(token["groups"]))

            return token



class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
