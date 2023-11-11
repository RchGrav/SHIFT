import argparse
import json
import os
import hashlib


def create_short_hash(text, parent_id=None, length=8):
    hash_input = (parent_id if parent_id else "") + text
    hash_object = hashlib.sha256(hash_input.encode())
    hex_dig = hash_object.hexdigest()
    return hex_dig[:length]

def updated_add_prompt(prompts_data, prompt, parent_id=None, metadata=None, children=None):
    hash_id = create_short_hash(prompt, parent_id)
    
    # Check if the prompt already exists
    if hash_id in prompts_data["prompts"]:
        return False  # Prompt already exists, do not add

    prompt_record = {
        "text": prompt,
        "metadata": metadata if metadata else {},
        "children": children if children else [],
        "parent": parent_id
    }
    prompts_data["prompts"][hash_id] = prompt_record

    # Update parent prompt if exists
    if parent_id and parent_id in prompts_data["prompts"]:
        parent_prompt = prompts_data["prompts"][parent_id]
        parent_prompt["children"].append(hash_id)
        prompts_data["prompts"][parent_id] = parent_prompt

    return True  # Prompt successfully added

def verify_prompt_hash(prompts_data, hash_id):
    if hash_id not in prompts_data["prompts"]:
        return False  # Prompt not found

    prompt = prompts_data["prompts"][hash_id]
    parent_id = prompt["parent"]
    reconstructed_hash = create_short_hash(prompt["text"], parent_id)

    if reconstructed_hash != hash_id:
        return False  # Hash mismatch

    if not parent_id:
        return True  # Root prompt

    return verify_prompt_hash(prompts_data, parent_id)


def print_help_menu():
    help_text = """
    Usage Examples:
    ---------------
    # Add a root prompt
    python cli_script.py --add "Discuss the importance of space exploration." --metadata '{"category": "Space", "rating": 95}'

    # Add a child prompt
    python cli_script.py --add "What are the benefits of sending humans to Mars?" --parent "parent_hash_id"

    # Verify a prompt
    python cli_script.py --verify "prompt_hash_id"

    # Print help menu
    python cli_script.py --help
    """
    print(help_text)

def main():
    parser = argparse.ArgumentParser(description='Manage a collection of prompts in a DAG structure.')
    parser.add_argument('--add', type=str, help='Add a new prompt')
    parser.add_argument('--parent', type=str, help='Parent ID of the prompt')
    parser.add_argument('--metadata', type=str, help='Metadata for the prompt in JSON format')
    parser.add_argument('--verify', type=str, help='Verify the integrity of a prompt by its hash ID')
    parser.add_argument('--help', action='store_true', help='Print help menu')

    args = parser.parse_args()

    # Load or initialize prompts_data
    prompts_file = 'prompts_data.json'
    if os.path.exists(prompts_file):
        with open(prompts_file, 'r') as file:
            prompts_data = json.load(file)
    else:
        prompts_data = {"prompts": {}}

    if args.help:
        print_help_menu()
    elif args.add:
        metadata = json.loads(args.metadata) if args.metadata else None
        result = updated_add_prompt(prompts_data, args.add, parent_id=args.parent, metadata=metadata)
        if result:
            print(f"Prompt added successfully. ID: {create_short_hash(args.add, args.parent)}")
        else:
            print("Failed to add prompt. It may already exist.")
    elif args.verify:
        if verify_prompt_hash(prompts_data, args.verify):
            print(f"Prompt ID {args.verify} is verified.")
        else:
            print(f"Prompt ID {args.verify} verification failed.")

    # Save prompts_data back to file
    with open(prompts_file, 'w') as file:
        json.dump(prompts_data, file, indent=2)

if __name__ == "__main__":
    main()
