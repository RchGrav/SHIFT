
import hashlib
import json
import sys

def generate_hash(prompt, parent_id=None):
    hash_object = hashlib.sha256()
    if parent_id:
        hash_object.update(parent_id.encode())
    hash_object.update(prompt.encode())
    return hash_object.hexdigest()

def add_prompt(prompt, parent_id=None):
    hash_id = generate_hash(prompt, parent_id)
    prompt_record = {
        "text": prompt,
        "metadata": {},
        "children": [],
        "parent": parent_id
    }
    try:
        with open('shift.json', 'r+') as file:
            data = json.load(file)
            if hash_id in data['prompts']:
                print("Duplicate prompt detected.")
                return
            data['prompts'][hash_id] = prompt_record
            file.seek(0)
            json.dump(data, file, indent=4)
            print("Prompt added successfully.")
    except FileNotFoundError:
        with open('shift.json', 'w') as file:
            json.dump({"prompts": {hash_id: prompt_record}}, file, indent=4)
            print("Prompt added successfully.")

def verify_chain(hash_id):
    try:
        with open('shift.json', 'r') as file:
            data = json.load(file)
            prompt = data['prompts'].get(hash_id)
            if not prompt:
                print("Prompt not found.")
                return False
            while prompt['parent']:
                if prompt['parent'] not in data['prompts']:
                    print("Broken chain detected.")
                    return False
                prompt = data['prompts'][prompt['parent']]
            print("Chain verified successfully.")
            return True
    except FileNotFoundError:
        print("shift.json file not found.")
        return False

def print_help():
    help_text = '''
    SHIFT Command Line Interface

    Commands:
    add "<prompt>" "<parent_id>": Add a new prompt with an optional parent ID.
    verify "<hash_id>": Verify the chain of a prompt based on its hash ID.
    help: Show this help message.
    '''
    print(help_text)

def main():
    if len(sys.argv) < 2 or sys.argv[1] == 'help':
        print_help()
        return

    command = sys.argv[1]

    if command == 'add':
        if len(sys.argv) < 3:
            print("Please provide a prompt to add.")
            return
        prompt = sys.argv[2]
        parent_id = None if len(sys.argv) < 4 else sys.argv[3]
        add_prompt(prompt, parent_id)

    elif command == 'verify':
        if len(sys.argv) < 3:
            print("Please provide a hash ID to verify.")
            return
        hash_id = sys.argv[2]
        verify_chain(hash_id)

    else:
        print("Unknown command. Type 'help' for a list of commands.")

if __name__ == "__main__":
    main()
