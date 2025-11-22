import logging

logger = logging.getLogger(__name__)
handler = logging.StreamHandler('requests.log')
formatter = logging.Formatter(fmt = "%(asctime)s %(levelname)s: %(message)s")
handler.formatter = formatter
logger.addHandler(handler)
logger.setLevel(logging.INFO)


class RequestLoggingMiddleware:
    """Custom middleware class to log request"""
    def __init__(self, get_response):
        """Initializing the class"""
        self.get_response = get_response


    def __call__(self, request):
        """Function to make the class callable"""

        logger.info(f'-User:{request.user}-Path:{request.path}')

        response = self.get_response(request)

        return response