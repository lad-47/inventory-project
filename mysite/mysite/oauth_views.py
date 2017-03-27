from urllib.parse import urlencode
from requests.api import request as req
from requests.exceptions import RequestException
import json
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.core.urlresolvers import reverse
from django.http import HttpResponse

#def redirect(request):
#    url='https://oauth.oit.duke.edu/oauth/authorize.php'
#    args = {
#        'client_id': 'inventory',
#        'redirect_uri': 'https://colab-sbx-44.oit.duke.edu/accounts/callback/duke/',
#        'response_type': 'code',
#        'scope': 'identity:netid:read'
#    }
#    params = urlencode(args)
#    return HttpResponse('{0}?{1}'.format(url, params))
    

def callback(request):
    if 'code' in request.GET:
        args = {
            'client_id': 'inventory',
            'redirect_uri': 'https://colab-sbx-44.oit.duke.edu/accounts/callback/duke/',
            'client_secret': 'W@@bwwQubNDbkv9E*W6w4+%SSY42Ps4quP4qKJPDLP5tHr+Gyz',
            'code': request.GET['code'],
            'grant_type': 'authorization_code',
        }
    try:
        response = req('post', 'https://oauth.oit.duke.edu/oauth/token.php', data=args)
        response.raise_for_status()
    except RequestException as e:
        return HttpResponse("bad")
    else:
        token_data = json.loads(response.text)
        token = token_data.get('access_token', None)
        url = 'https://api.colab.duke.edu/identity/v1/'
        headers = {
            'Accept': 'application/json',
            'x-api-key': 'inventory',
            'Authorization': 'Bearer '+token          
        }

        r = req('get',url, headers=headers)
        id_data = json.loads(r.text)
        netid = id_data.get('netid', None)
        try:
            user = User.objects.get(username=netid)
        except User.DoesNotExist:
            user = User.objects.create_user(netid, netid+'@duke.edu', 'password')
            user.password='none'
            user.save()
        #user = authenticate(username=netid, password='password')
        user = User.objects.get(username=netid)
        login(request,user)
        return HttpResponse('<a href="https://colab-sbx-44.oit.duke.edu">Logged In!</a>')