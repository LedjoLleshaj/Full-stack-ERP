from rest_framework.views import exception_handler as drf_exception_handler


def api_exception_handler(exc, context):
    response = drf_exception_handler(exc, context)
    if response is None:
        return None

    if isinstance(response.data, list):
        message = response.data[0] if response.data else str(exc)
    elif isinstance(response.data, dict):
        if "detail" in response.data:
            message = response.data["detail"]
        else:
            message = response.data
    else:
        message = str(response.data)

    error_code = getattr(exc, "default_code", None) or response.status_text.lower().replace(" ", "_")

    response.data = {
        "error": {
            "message": message,
            "code": error_code,
        }
    }
    return response
