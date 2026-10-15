from django.db import connection
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from drf_spectacular.utils import OpenApiResponse, extend_schema


@extend_schema(
    responses=OpenApiResponse(description="Service and database status."),
)

@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    database = "ok"
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception:
        database = "unavailable"
    return Response({"status": "ok", "database": database})
