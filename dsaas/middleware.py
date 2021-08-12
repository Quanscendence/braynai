import gc 
import logging



class GCMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        gc.disable()
        # the view (and later middleware) are called.

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.
        logging.info("before collection "+str(gc.get_count()))
        gc.collect()
        logging.info("after collection "+str(gc.get_count()))
        gc.enable()

        return response