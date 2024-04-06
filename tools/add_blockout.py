from setup import pick_context
from api_pco import PCOContext, services_get_all_people

def main():
    context = pick_context()
    pco = PCOContext(context['application_id'], context['secret'])
    print(services_get_all_people(pco))

if __name__ == '__main__':
    main()