from django.http import JsonResponse
from django.core.exceptions import RequestDataTooBig


class CheckRequest(object):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        response = self.get_response(request)

        return response

    def process_exception(self, request, exception):
        if isinstance(exception, RequestDataTooBig):
            return JsonResponse({"error_msg":"File size exceeds limit. File size should be 30MB or less"})