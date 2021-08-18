from django.dispatch import receiver
from django_auth_ldap.backend import populate_user
from django_auth_ldap.backend import LDAPBackend

from sso.helpers.Log import Log


@receiver(populate_user, sender=LDAPBackend)
def customUserPopulate(user, ldap_user=None, **kwargs):
    # This signal handler in order to customize the mapping - see AUTH_LDAP_USER_ATTR_MAP in settings.py.
    # https://django-auth-ldap.readthedocs.io/en/latest/reference.html#django_auth_ldap.backend.populate_user

    # Attributes from LDAP.
    if "uidNumber" in ldap_user.attrs:
        ldapAttributes = {
            "uid": ldap_user.attrs.get('uid')[0], # username.
            "uidNumber": ldap_user.attrs.get('uidNumber')[0] # unique id.
        }

        # Get user model from LDAPBackend.
        ldpb = LDAPBackend()
        u = ldpb.get_user_model()

        # Save into user model.
        for k, v in ldapAttributes.items():
            setattr(u, k, v.encode('utf-8'))
