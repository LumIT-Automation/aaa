from django.conf import settings

from sso.helpers.Log import Log


class Superadmin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def list() -> dict:
        o = {
            "items": list()
        }

        try:
            for idGroup in settings.SUPERADMIN_IDENTITY_AD_GROUPS:
                o["items"].append(idGroup)

        except Exception as e:
            raise e

        return o
