import json
import urllib.request


class AuthSign:

    def __init__(self, site, username, password):
        self.site = site
        self.username = username
        self.password = password

        self.expiration_date = None
        self.hash = None

        if self.site == 'viewmmasr':
            self.url = 'https://www.MMA-TV.net/loginForm.php'
        else:
            self.url = 'https://auth.smoothstreams.tv/hash_api.php'

    def fetch_hash(self):

        hash_url = f'{self.url}?username={self.username}&password={self.password}&site={self.site}'
        response = urllib.request.urlopen(hash_url)

        try:
            as_json = json.loads(response.read())

            if 'hash' in as_json:
                self.hash = as_json['hash']
                self.expiration_date = as_json['valid']

        except Exception as e:
            print('error!')

