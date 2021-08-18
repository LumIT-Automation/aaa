from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.reverse import reverse


class RootController(APIView):
    def get(self, request: Request) -> Response:
        return Response({
            'token': reverse('token', request=request),
            'token-refresh': reverse('token-refresh', request=request),
        })
