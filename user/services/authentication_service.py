import functools
import requests
from django.shortcuts import HttpResponse
from django.http import HttpResponseForbidden
from keycloak import KeycloakOpenID
from authlib.jose import jwt


class TokenAuthentication:
    def __init__(self, access_token):
        self.access_token = access_token
        self.public_key = self._get_keycloak_public_key()

    def _get_keycloak_public_key(self):
        keycloak_url = "http://localhost:8080/auth/realms/master"
        response = requests.get(keycloak_url)
        key_data = response.json()
        formatted_public_key = f"-----BEGIN PUBLIC KEY-----\n{key_data['public_key']}\n-----END PUBLIC KEY-----"
        return formatted_public_key

    def is_valid_token(self):
        if self.access_token:
            try:
                public_key = self.public_key
                publicKeyBinary = public_key.encode("ascii")
                token_data = jwt.decode(self.access_token, publicKeyBinary)
                return True
            except Exception as ex:
                return False
        else:
            return False


def token_verify(view_func):
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        access_token = request.META.get("HTTP_AUTHORIZATION", "").replace("Bearer ", "")
        given_auth = TokenAuthentication(access_token)
        if given_auth.is_valid_token():
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponseForbidden(
                "You do not have permission to access this resource."
            )

    return wrapper
