from rest_framework.views import exception_handler


def strict_exception_handler(exc, context):
    # сначала вызовем стандартный обработчик DRF, чтобы он сам посчитал
    response = exception_handler(exc, context)

    # если ошибка
    if response is not None:
        if response.status_code == 400:
            error_code = "validation_failed"
        elif response.status_code == 401:
            error_code - "unauthorized"
        elif response.status_code == 403:
            error_code = "permission_denied"
        elif response.status_code == 404:
            error_code = "not_found"
        else:
            error_code = "server_error"

        custom_response = {"error_code": error_code, "details": response.data}

        # перезаписываем стандартный ответ нашим
        response.data = custom_response
    return response
