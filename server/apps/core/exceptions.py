from rest_framework import status
from rest_framework.views import exception_handler


def api_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return None

    if isinstance(response.data, dict) and "error" in response.data:
        return response

    if response.status_code == status.HTTP_400_BAD_REQUEST:
        code, message = "VALIDATION_ERROR", "Dữ liệu không hợp lệ."
        details = response.data if isinstance(response.data, dict) else {"non_field_errors": response.data}
    elif response.status_code == status.HTTP_401_UNAUTHORIZED:
        code, message = "AUTHENTICATION_ERROR", "Thông tin xác thực không hợp lệ."
        details = response.data if isinstance(response.data, dict) else {"detail": response.data}
    elif response.status_code == status.HTTP_403_FORBIDDEN:
        code, message = "PERMISSION_DENIED", "Bạn không có quyền thực hiện thao tác này."
        details = response.data if isinstance(response.data, dict) else {"detail": response.data}
    elif response.status_code == status.HTTP_404_NOT_FOUND:
        code, message = "NOT_FOUND", "Không tìm thấy tài nguyên."
        details = {}
    elif response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED:
        code, message = "METHOD_NOT_ALLOWED", "Phương thức không được hỗ trợ."
        details = {}
    elif response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
        code, message = "RATE_LIMITED", "Bạn đã gửi quá nhiều yêu cầu."
        details = {}
    else:
        code, message = "API_ERROR", "Không thể xử lý yêu cầu."
        details = response.data if isinstance(response.data, dict) else {"detail": response.data}

    response.data = {"error": {"code": code, "message": message, "details": details}}
    return response
