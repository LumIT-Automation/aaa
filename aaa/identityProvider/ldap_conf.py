import ldap
from django_auth_ldap.config import LDAPSearch, LDAPGroupQuery, LDAPGroupType, GroupOfNamesType, PosixGroupType


# URI.

AUTH_LDAP_SERVER_URI = "ldap://10.0.111.111:389"

# SETTINGS.
AUTH_LDAP_CONNECTION_OPTIONS = {
    ldap.OPT_DEBUG_LEVEL: 1,
    ldap.OPT_NETWORK_TIMEOUT: 10,
    ldap.OPT_TIMEOUT: 10,
}

AUTH_LDAP_BIND_DN = "CN=admin,DC=lab,DC=local"
AUTH_LDAP_BIND_PASSWORD = "password"

AUTH_LDAP_USER_SEARCH = LDAPSearch("ou=monkeys,dc=lab,dc=local",
    ldap.SCOPE_SUBTREE, "(uid=%(user)s)"
)

AUTH_LDAP_GROUP_SEARCH = LDAPSearch(
    "dc=monkeys,dc=lab,dc=local",
    ldap.SCOPE_SUBTREE,
    "(objectClass=groupOfNames)",
)

AUTH_LDAP_GROUP_TYPE = GroupOfNamesType(name_attr="ou")

AUTH_LDAP_USER_ATTR_MAP = {
    "first_name": "givenName",
    "last_name": "",
    "email": "mail",
    "uid": "uidNumber",
    # extend using django_auth_ldap.backend.populate_user signal's listener: see sso/__init__'s customUserPopulate().
}

# AUTH_LDAP_USER_FLAGS_BY_GROUP = {
#    "is_active": LDAPGroupQuery("dc=lab,dc=local"),
#    "is_superuser": "dc=lab,dc=local",
# }

AUTH_LDAP_ALWAYS_UPDATE_USER = True
AUTH_LDAP_NO_NEW_USERS = False
AUTH_LDAP_FIND_GROUP_PERMS = True
AUTH_LDAP_CACHE_TIMEOUT = 1
