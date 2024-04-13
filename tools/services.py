from datetime import datetime
from setup import pick_context, pick_names, get_blockout_info
from api_pco import PCOContext, services_get_all_people, services_post_blockout, services_get_recent_plans, services_get_team_members_of_plan

def find_person_and_input_blockout(pco: PCOContext, all_people, blockout_user, blockout):
    match_found = False
    for page in all_people:
        for services_user in page['data']:
            if blockout_user['Full Name'] == services_user['attributes']['full_name']:
                #print(f'Found a Full Name match for {missionary["Full Name"]}')
                services_post_blockout(pco, services_user['id'], blockout['starts_at'], blockout['ends_at'], blockout['reason'])
                match_found = True
            elif blockout_user['First Name'] == services_user['attributes']['first_name'] and blockout_user['Last Name'] == services_user['attributes']['last_name']:
                #print(f'Found a First Name and Last Name match for {missionary["Full Name"]}')
                services_post_blockout(pco, services_user['id'], blockout['starts_at'], blockout['ends_at'], blockout['reason'])
                match_found = True
            elif blockout_user['First Name'] == services_user['attributes']['full_name'].split(' ')[0] and blockout_user['Last Name'] == services_user['attributes']['full_name'].split(' ')[-1]:
                #print(f'Found a unique First Name and Last Name match for {missionary["Full Name"]}')
                services_post_blockout(pco, services_user['id'], blockout['starts_at'], blockout['ends_at'], blockout['reason'])
                match_found = True
            if match_found:
                break
        if match_found:
            break
    else:
        print(f'No match found for {blockout_user["Full Name"]}')

def add_blockout(pco: PCOContext):
    """
    Adds blockout dates for individuals in Planning Center Services based on provided names and blockout information.
    
    Retrieves application context and fetches all people from the services. It attempts to match each person with
    the given names list and adds blockout periods if matches are found. Outputs a message for any names without
    matching records or missing blockout information.
    
    Returns:
        None
    """
    names = pick_names()
    blockouts = get_blockout_info()
    pco = PCOContext(context['application_id'], context['secret'])
    all_people = services_get_all_people(pco)

    for blockout_user in names:
        blockout_user['First Name'] = blockout_user['Full Name'].split(' ')[0]
        blockout_user['Last Name'] = blockout_user['Full Name'].split(' ')[-1]
        trip = blockout_user['Trip']
        if trip not in blockouts:
            print(f'No blockout information found for {trip}')
            continue

        find_person_and_input_blockout(pco, all_people, blockout_user, blockouts[trip])

def check_for_duplicates(pco: PCOContext):
    """
    Checks for duplicate volunteers in upcoming plans.

    Retrieves application context and fetches all plans from the services. It then retrieves all volunteers for each
    plan and checks for duplicates. Outputs a message for any duplicate volunteers found.

    Returns:
        None
    """
    pco = PCOContext(context['application_id'], context['secret'], context['service_id'])
    plans = services_get_recent_plans(pco)
    today = datetime.now()
    print(today)

    for plan in plans['data']:
        # Check if the plan is in the future, break if the plan has passed
        plan_date = datetime.strptime(plan['attributes']['sort_date'], '%Y-%m-%dT%H:%M:%SZ')

        if plan_date < today:
            break
            
        print(f"Plan: {plan['attributes']['sort_date']}")
        all_volunteers = services_get_team_members_of_plan(pco, plan['id'])
        
        # Check if there are duplicates in the volunteers
        volunteers = []
        for page in all_volunteers:
            for volunteer in page['data']:
                if volunteer['attributes']['name'] in volunteers:
                    print(f'Duplicate volunteer: {volunteer['attributes']['name']}')
                volunteers.append(volunteer['attributes']['name']) 

if __name__ == '__main__':
    context = pick_context()
    option = input('What would you like to do?\n1. Add blockouts\n2. Check for duplicates\n')
    if option == '1':
        add_blockout(context)
    elif option == '2':
        check_for_duplicates(context)
    else:
        print('Invalid option')