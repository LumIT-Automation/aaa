import ldap
from django_auth_ldap.config import LDAPSearch, LDAPGroupQuery, LDAPGroupType, GroupOfNamesType, PosixGroupType, LDAPSearchUnion, ActiveDirectoryGroupType, NestedActiveDirectoryGroupType

ldap.set_option(ldap.OPT_REFERRALS, 0)


# URI.
AUTH_LDAP_SERVER_URI = "ldap://10.0.111.110:389"

# SETTINGS.

AUTH_LDAP_BIND_DN = "CN=adToken,CN=Users,DC=lab,DC=local"
AUTH_LDAP_BIND_PASSWORD = "password"

AUTH_LDAP_BIND_AS_AUTHENTICATING_USER = True

AUTH_LDAP_USER_SEARCH = LDAPSearchUnion(
    LDAPSearch("CN=Users,DC=lab,DC=local", ldap.SCOPE_SUBTREE, "(sAMAccountName=%(user)s)"),
    LDAPSearch("CN=Users,DC=lab,DC=local", ldap.SCOPE_SUBTREE, "userPrincipalName=%(user)s")
)

AUTH_LDAP_GROUP_SEARCH = LDAPSearch(
    "CN=Users,DC=lab,DC=local",
    ldap.SCOPE_SUBTREE,
    "(objectClass=group)",
)

# Simple group required configuration
# AUTH_LDAP_GROUP_TYPE = GroupOfNamesType(name_attr="ou")
# AUTH_LDAP_REQUIRE_GROUP = "CN=groupRequired,CN=Users,DC=lab,DC=local"

# Group of groups configuration (required nested groups)
AUTH_LDAP_GROUP_TYPE = NestedActiveDirectoryGroupType()
AUTH_LDAP_REQUIRE_GROUP = ( LDAPGroupQuery("CN=groupGranPa,CN=Users,DC=lab,DC=local"))

AUTH_LDAP_USER_QUERY_FIELD = "username"
AUTH_LDAP_USER_ATTR_MAP = {
    "username": "userPrincipalName",
    "first_name": "givenName",
    "last_name": "",
    "email": "mail",
    # extend using django_auth_ldap.backend.populate_user signal's listener: see sso/__init__'s customUserPopulate().
}


AUTH_LDAP_ALWAYS_UPDATE_USER = True
AUTH_LDAP_NO_NEW_USERS = False
AUTH_LDAP_FIND_GROUP_PERMS = True
AUTH_LDAP_CACHE_TIMEOUT = 1
