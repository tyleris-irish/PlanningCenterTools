import json
from datetime import datetime, timezone
from setup import pick_context
from api_pco import PCOContext, services_get_recent_plans, services_get_team_members_of_plan

def main():
    context = pick_context()
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
    main()