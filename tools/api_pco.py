import requests
import json
import datetime
from setup import pick_context

class PCOContext:
    def __init__(self, app_id, secret, service_id):
        self.base_url = 'https://api.planningcenteronline.com'
        self.app_id = app_id
        self.secret = secret
        self.service = service_id
        self.auth = (self.app_id, self.secret)
        self.verify = True

def services_get_all_people(context: PCOContext) -> list:
    """
    Retrieves all people in services.

    Args:
        context (PCOContext): The PCOContext object containing the base URL, authentication, and verification settings.

    Returns:
        list: A list of dictionaries containing the response data for each page of people.
    """
    link = context.base_url + '/services/v2/people?order=last_name&per_page=100&offset=0'

    data = []
    while True:
        response = requests.get(link, auth=context.auth, verify=context.verify)
        if response.status_code != 200:
            print(f'Error retrieving people: {response.text}')
            break

        response_data = response.json()
        data.append(response_data)

        if not response_data['links'].get('next'):
            break

        link = response_data['links']['next']

    return data

def services_post_blockout(context: PCOContext, person_id:str, start_time:str, end_time:str, reason:str):
    """
    Adds a blockout for a volunteer.

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

def services_get_recent_plans(context: PCOContext):
    """
    Retrieves all plans for a specified service type. Sorted by latest plan date.

    Args:
        context (PCOContext): The PCOContext object containing the base URL, authentication, and verification settings.
        service_type_id (str): The ID of the service type for which plans are being retrieved.
        plan_id (str): The ID of the plan for which team members are being retrieved.

    Returns:
        list: A list of dictionaries containing the response data for each page of plans.
    """
    link = context.base_url + f'/services/v2/service_types/{context.service}/plans?order=-sort_date'

    response = requests.get(link, auth=context.auth, verify=context.verify)

    if response.status_code != 200:
        print(f'Error retrieving plans: {response.text}')
        return []
    
    return response.json()

def services_get_team_members_of_plan(context: PCOContext, service_type_id:str, plan_id:str):
    """
    Retrieves all team members in a plan.

    Args:
        context (PCOContext): The PCOContext object containing the base URL, authentication, and verification settings.
        service_type_id (str): The ID of the service type for which team members are being retrieved.
        plan_id (str): The ID of the plan for which team members are being retrieved.

    Returns:
        list: A list of dictionaries containing the response data for each page of team members.
    """
    link = context.base_url + f'/services/v2/service_types/{service_type_id}/plans/{plan_id}/team_members'

    data = []
    while True:
        response = requests.get(link, auth=context.auth, verify=context.verify)
        response_data = response.json()
        data.append(response_data)

        if not response_data['links'].get('next'):
            break

        link = response_data['links']['next']

    return data

def main():
    context = pick_context()
    pco = PCOContext(context['application_id'], context['secret'], service_id = context['service_id'])

    # test getting all people
    people = list(services_get_all_people(pco))
    filename = 'output/' + '{:%Y%m%d-%H%M%S}'.format(datetime.datetime.now()) + '-people-dump.json'
    with open(filename, 'w') as json_file:
        json_file.write(json.dumps(list(people), indent=4, sort_keys=True))
    print(f'Output written to {filename}')

    # get amount of people in each call
    for call in list(people):
        for person in call['data']:
            print(person['attributes']['first_name'], person['attributes']['last_name'])

    # test getting recently created services
    plans = services_get_recent_plans(pco)
    filename = 'output/' + '{:%Y%m%d-%H%M%S}'.format(datetime.datetime.now()) + '-recent-plans-dump.json'
    with open(filename, 'w') as json_file:
        json_file.write(json.dumps(plans, indent=4, sort_keys=True))
    print(f'Output written to {filename}')

    # test getting team members of a plan
    plan_id = plans['data'][0]['id']
    team_members = services_get_team_members_of_plan(pco, context['service_id'], plan_id)
    filename = 'output/' + '{:%Y%m%d-%H%M%S}'.format(datetime.datetime.now()) + '-team-members-dump.json'
    with open(filename, 'w') as json_file:
        json_file.write(json.dumps(team_members, indent=4, sort_keys=True))
    print(f'Output written to {filename}')

if __name__ == '__main__':
    main()