import re
from django.conf import settings

from django.http import FileResponse

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status


from sso.controllers.CustomController import CustomController
from sso.helpers.Exception import CustomException

from sso.helpers.Log import Log



########################################################################################################################
# Txt file.
########################################################################################################################

class SsoRawTxtController(CustomController):
    @staticmethod
    def get(request: Request, fileName: str = "") -> Response:
        actionLog = f"Get file {fileName} from folder {settings.DOC_TXT_DIR}."
        fileName = settings.DOC_TXT_DIR + fileName

        try:
            user = CustomController.loggedUser(request)
            if SsoRawTxtController.checkRequestedFile(fileName):
                Log.actionLog(actionLog, user)
                try:
                    f = open(fileName, "r")
                except FileNotFoundError:
                    raise CustomException(status=400, payload={"Sso": "Requested file not found."})

                response = FileResponse(f, as_attachment=True)
            else:
                response = Response(None, status=status.HTTP_403_FORBIDDEN)

        except FileNotFoundError:
            raise CustomException(status=400, payload={"Sso": "Requested file not found."})


        except Exception as e:
            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return response



    @staticmethod
    def checkRequestedFile(fileName: str) -> bool:
        try:
            if re.match('^.*\.(txt|yaml|json)$', fileName):
                return True

            return False
        except Exception as e:
            raise e

