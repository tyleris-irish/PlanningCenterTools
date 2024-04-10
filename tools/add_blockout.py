from setup import pick_context, pick_names, get_blockout_info
from api_pco import PCOContext, services_get_all_people, services_add_blockout

def main():
    context = pick_context()
    names = pick_names()
    blockouts = get_blockout_info()
    pco = PCOContext(context['application_id'], context['secret'], context['organization_id'])
    all_people = services_get_all_people(pco)

    for missionary in names:
        missionary['First Name'] = missionary['Full Name'].split(' ')[0]
        missionary['Last Name'] = missionary['Full Name'].split(' ')[-1]
        trip = missionary['Trip']
        if trip not in blockouts:
            print(f'No blockout information found for {trip}')
            continue

        match_found = False
        for page in all_people:
            for volunteer in page['data']:
                if missionary['Full Name'] == volunteer['attributes']['full_name']:
                    #print(f'Found a Full Name match for {missionary["Full Name"]}')
                    services_add_blockout(pco, volunteer['id'], blockouts[trip]['starts_at'], blockouts[trip]['ends_at'], blockouts[trip]['reason'])
                    match_found = True
                    break
                elif missionary['First Name'] == volunteer['attributes']['first_name'] and missionary['Last Name'] == volunteer['attributes']['last_name']:
                    #print(f'Found a First Name and Last Name match for {missionary["Full Name"]}')
                    services_add_blockout(pco, volunteer['id'], blockouts[trip]['starts_at'], blockouts[trip]['ends_at'], blockouts[trip]['reason'])
                    match_found = True
                    break
                elif missionary['First Name'] == volunteer['attributes']['full_name'].split(' ')[0] and missionary['Last Name'] == volunteer['attributes']['full_name'].split(' ')[-1]:
                    #print(f'Found a unique First Name and Last Name match for {missionary["Full Name"]}')
                    services_add_blockout(pco, volunteer['id'], blockouts[trip]['starts_at'], blockouts[trip]['ends_at'], blockouts[trip]['reason'])
                    match_found = True
                    break
            if match_found:
                break
        if not match_found:
            print(f'No match found for {missionary["Full Name"]}')
        



if __name__ == '__main__':
    main()