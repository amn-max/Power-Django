import logging
from django.http import HttpRequest
from rest_framework.views import APIView


class LoggingMixin:
    """
    Provides full logging of requests and responses for both class-based and function-based views
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger("django.request")

    def log_request_data(self, request):
        try:
            self.logger.debug(
                {
                    "request": request.data,
                    "method": request.method,
                    "endpoint": request.path,
                    "user": request.user.username,
                    "ip_address": request.META.get("REMOTE_ADDR"),
                    "user_agent": request.META.get("HTTP_USER_AGENT"),
                }
            )
        except Exception:
            self.logger.exception("Error logging request data")

    def log_response_data(self, request, response):
        try:
            self.logger.debug(
                {
                    "response": response.data,
                    "status_code": response.status_code,
                    "user": request.user.username,
                    "ip_address": request.META.get("REMOTE_ADDR"),
                    "user_agent": request.META.get("HTTP_USER_AGENT"),
                }
            )
        except Exception:
            self.logger.exception("Error logging response data")

    def initial(self, request, *args, **kwargs):
        if isinstance(self, APIView):  # Check if the view is a class-based view
            self.log_request_data(request)
        super().initial(request, *args, **kwargs)

    def finalize_response(self, request, response, *args, **kwargs):
        if isinstance(self, APIView):  # Check if the view is a class-based view
            self.log_response_data(request, response)
        return super().finalize_response(request, response, *args, **kwargs)

    def __call__(self, request, *args, **kwargs):
        if isinstance(
            request, HttpRequest
        ):  # Check if the view is a function-based view
            self.log_request_data(request)
        response = super().__call__(request, *args, **kwargs)
        if isinstance(
            request, HttpRequest
        ):  # Check if the view is a function-based view
            self.log_response_data(request, response)
        return response
