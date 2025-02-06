import requests
from django.http import Http404

from codds.settings import DISCORD_CLIENT_ID, DISCORD_CLIENT_SECRET, DISCORD_REDIRECT_URI


class Discord:
    """
    Discord class to fetch the user info and return it
    """

    @staticmethod
    def exchange_code(code):
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': DISCORD_REDIRECT_URI
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        r = requests.post('https://discord.com/api/v10/oauth2/token', data=data, headers=headers, auth=(DISCORD_CLIENT_ID, DISCORD_CLIENT_SECRET))

        if r.status_code != 200:
            raise Http404("Invalid code")

        # Returns {token_type, access_token, refresh_token, expires_in, scope}
        return r.json()

    @staticmethod
    def get_user_data(access_token):
        r = requests.get('https://discord.com/api/v10/users/@me', headers={'Authorization': f'Bearer {access_token}'})
        return r.json()
