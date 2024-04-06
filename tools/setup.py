import glob
import json

def grab_all_contexts():
    contexts = {}
    # navigate to ./context and grab each .cxt file
    for cxt in glob.glob('context/*.cxt'):
        # open the file and read the contents
        with open(cxt, 'r') as json_file:
            context = json.load(json_file)
            file_name = cxt.split('/')[-1].split('.')[0]
            contexts[file_name] = context
    
    if not contexts:
        print('No contexts found. Please create a {name}.cxt file in the context directory.')
        print('Input the values you get from https://developer.planning.center/, follow the same structure as the example context')
        exit(1)
    
    return contexts

def pick_context():
    contexts = grab_all_contexts()
    print('Choose a context to use:')
    for i, context in enumerate(contexts):
        print(f'{i+1}. {context}')
    choice = input('Enter the number of the context you want to use: ')
    try:
        return contexts[list(contexts.keys())[int(choice)-1]]
    except:
        print('Invalid choice. Please enter a number from the list.')
        return pick_context()

if __name__ == '__main__':
    print(pick_context())