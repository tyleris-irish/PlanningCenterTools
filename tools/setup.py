import glob
import json
import csv

def grab_all_contexts() -> dict:
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

def pick_context() -> dict:
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
    
def get_blockout_info() -> dict:
    blockouts_file = 'input/blockouts.json'
    with open(blockouts_file, 'r') as json_file:
        blockouts = json.load(json_file)
    return blockouts

def grab_all_names() -> dict:
    name_files = {}
    # navigate to ./names and grab each csv file
    for name_file in glob.glob('input/*.csv'):
        # open the file and read the contents
        with open(name_file, 'r') as csv_file:
            # convert file to json
            file = csv_file.read()
            csv_dict = csv.DictReader(file.splitlines())
            data = [row for row in csv_dict]
            # get file name
            file_name = name_file.split('/')[-1].split('.')[0]
            name_files[file_name] = data
    
    if not name_files:
        print('No names found. Please create a {name}.csv file in the names directory.')
        print('Input the values you get from https://developer.planning.center/, follow the same structure as the example name')
        exit(1)
    
    return name_files

def pick_names() -> str:
    names = grab_all_names()
    print('Choose a names file to use:')
    for i, name in enumerate(names):
        print(f'{i+1}. {name}')
    choice = input('Enter the number of the names file you want to use: ')
    try:
        return names[list(names.keys())[int(choice)-1]]
    except:
        print('Invalid choice. Please enter a number from the list.')
        return pick_names()


if __name__ == '__main__':
    print(pick_context())