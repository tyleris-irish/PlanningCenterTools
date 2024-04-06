import requests

class PCOContext:
    def __init__(self, app_id, secret):
        self.base_url = 'https://api.planningcenteronline.com'
        self.app_id = app_id
        self.secret = secret
        self.auth = (self.app_id, self.secret)
        self.verify = True

def services_get_all_people (context: PCOContext):
    link = '/services/v2/people?order=last_name'

    response = requests.get(context.base_url + link, auth=context.auth, verify=context.verify)

    return response.json()
