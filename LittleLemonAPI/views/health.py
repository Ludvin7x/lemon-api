from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from ..throttles import HealthzThrottle 
class HealthCheckView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [HealthzThrottle] 

    def get(self, request):
        return Response({"status": "OK"})
