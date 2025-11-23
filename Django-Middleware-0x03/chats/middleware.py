import logging
from time import time
from datetime import datetime
from django.http import JsonResponse
from django.utils.timezone import now
from django.core.cache import cache # Helping in persistent storage of the sender_id


logger = logging.getLogger(__name__)
logging.basicConfig(filename='requests.log', encoding='utf-8', level=logging.DEBUG)
formatter = logging.Formatter(fmt = "%(asctime)s %(levelname)s: %(message)s")
logger.setLevel(logging.INFO)

CRITICAL_ACTION = 'DELETE'


class RequestLoggingMiddleware:
    """Custom middleware class to log request"""
    def __init__(self, get_response):
        """Initializing the class"""
        self.get_response = get_response


    def __call__(self, request):
        """Function to make the class callable"""

        logger.info(f'{datetime.now()}-User:{request.user}-Path:{request.path}')

        response = self.get_response(request)

        return response


class RestrictAccessByTimeMiddleware:
    """Custom middleware to restrict messaging by time"""
    def __init__(self, get_response):
        """Initializing the class"""
        self.get_response = get_response

    def __call__(self, request):
        """Function implementation"""
        if request.path.startswith('/api/conversations/messages/') \
        and request.method not in ['GET', 'HEAD'] \
        and now().hour not in range(18,22):
            return JsonResponse({
                'message': 'Can\'t access chat at this time'
            }, status = 403)
        return self.get_response(request)


class OffensiveLanguageMiddleware:
    """Custom to restrict spam messaging by a user"""
    def __init__(self, get_response):
        """Initializing the class"""
        self.get_response = get_response

    def __call__(self, request):
        """Function implementation
        This is a function that tracks the number of messages sent
        by a user limiting the maximum number sent in a minute to 
        5 messages
        """

        if request.method == 'POST':
            #We are trying to find the client
            sender_id = request.META.get("REMOTE_ADDR") \
                and request.path.startswith("/api/conversations/messages/") #add proxy server
            

            if not sender_id:
                #Handling instances where there is no sender id
                return JsonResponse({
                    'message':'No Sender Id'
                }, status = 403)
            

            rate_limit_key = f'ip: {sender_id}'
            limit = 5
            period = 60

            history = cache.get(rate_limit_key, [])
            current_time = time()


            history = [t for t in history if t > current_time-period]

            if len(history) >= limit:
                retry_after = int(period - (current_time - history[0])) if history else period
                response = JsonResponse({
                    'message':"You have made too many requests. \
                        Please try again later."
                        }, status = 429)
                response['Retry-After'] = retry_after
                return response
            
            history.append(current_time)
            cache.set(rate_limit_key, history, timeout=period)

        return self.get_response(request)


class RolepermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response


    def __call__(self, request):
        if request.user.role not in {'admin', 'moderator'}:
            if request.method == CRITICAL_ACTION:
                return JsonResponse({
                    'message':'Not in your clearance'
                }, status = 403)
        return self.get_response(request)
