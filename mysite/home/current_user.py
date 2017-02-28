from threading import local
from home.models import User

_user = local()

class CurrentUserMiddleware(object):
    def process_request(self, request):
        _user.value = request.user

def get_current_user():
	try:
		return _user.value
	except AttributeError:
		return User.objects.get(username="admin");