from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from sso.models.Superadmin import Superadmin

from sso.serializers.Superadmin import SuperadminSerializer as Serializer

from sso.controllers.CustomController import CustomController
from sso.helpers.Log import Log


class SuperadminsController(CustomController):
    @staticmethod
    def get(request: Request) -> Response:
        data = dict()
        itemData = dict()
        user = CustomController.loggedUser(request)

        try:
            Log.actionLog("Superadmin groups list", user)
            itemData["data"] = Superadmin.list()

            data["data"] = Serializer(itemData).data["data"]
            data["href"] = request.get_full_path()

            httpStatus = status.HTTP_200_OK

        except Exception as e:
            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(data, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })
