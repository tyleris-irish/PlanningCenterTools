import requests
import json
from setup import pick_context

class PCOContext:
    def __init__(self, app_id, secret, organization):
        self.base_url = 'https://api.planningcenteronline.com'
        self.app_id = app_id
        self.secret = secret
        self.organization = organization
        self.auth = (self.app_id, self.secret)
        self.verify = True

def services_get_all_people(context: PCOContext) -> list:
    """
    Retrieves all people from the Planning Center Services API.

    Args:
        context (PCOContext): The PCOContext object containing the base URL, authentication, and verification settings.

    Returns:
        list: A list of dictionaries containing the response data for each page of people.
    """
    link = context.base_url + '/services/v2/people?order=last_name&per_page=100&offset=0'

    data = []
    while True:
        response = requests.get(link, auth=context.auth, verify=context.verify)
        response_data = response.json()
        data.append(response_data)

        if not response_data['links'].get('next'):
            break

        link = response_data['links']['next']

    return data

def services_add_blockout(context: PCOContext, person_id:str, start_time:str, end_time:str, reason:str):
    """
    Adds a blockout for a person in the Planning Center Services API.

    Args:
        context (PCOContext): The PCOContext object containing the base URL, authentication, and verification settings.
        person_id (str): The ID of the person for whom the blockout is being added.
        start_time (str): The start time of the blockout in ISO 8601 format.
        end_time (str): The end time of the blockout in ISO 8601 format.
        reason (str): The reason for the blockout.

    Returns:
        None
    """
    link = context.base_url + f'/services/v2/people/{person_id}/blockouts'
    data = {
        "data": {
            "attributes": {
                "reason": reason,
                "repeat_frequency": "no_repeat",
                "starts_at": start_time,
                "ends_at": end_time,
                "share": "false"
            }
        }
    }
    response = requests.post(link, auth=context.auth, verify=context.verify, json=data)
    if response.status_code == 201:
        print(f'Blockout added for {person_id}')
    else:
        print(f'Error adding blockout for {person_id}')
        print(response.text)

def main():
    context = pick_context()
    pco = PCOContext(context['application_id'], context['secret'], context['organization_id'])

    # output the response from the API to a json file
    with open('output.json', 'w') as json_file:
        output = list(services_get_all_people(pco))
        json_file.write(json.dumps(list(output), indent=4, sort_keys=True))
        print('Output written to output.json')

        # get amount of people in each call
        for call in list(output):
            for person in call['data']:
                print(person['attributes']['first_name'], person['attributes']['last_name'])

if __name__ == '__main__':
    main()