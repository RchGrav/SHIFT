import os
import json
import hashlib

def create_short_hash(text, parent_id=None, length=8):
    """
    Create a short hash for a given text and an optional parent ID.

    Parameters:
    text (str): The text to be hashed.
    parent_id (str, optional): The parent ID to include in the hash. Defaults to None.
    length (int, optional): The length of the hash to return. Defaults to 8.

    Returns:
    str: A substring of the hex digest of the hash.
    """
    hash_input = (parent_id if parent_id else "") + text
    try:
        hash_object = hashlib.sha256(hash_input.encode())
        hex_dig = hash_object.hexdigest()
        return hex_dig[:length]
    except Exception as e:
        raise ValueError("Error in generating hash: " + str(e))

def add_prompt(prompts_data, prompt, parent_id=None, metadata=None, children=None):
    """
    Add a new prompt to the prompts data.

    Parameters:
    prompts_data (dict): The dictionary containing prompts data.
    prompt (str): The text of the prompt to add.
    parent_id (str, optional): The parent ID of the prompt. Defaults to None.
    metadata (dict, optional): Additional metadata for the prompt. Defaults to None.
    children (list, optional): List of children prompts. Defaults to None.

    Returns:
    bool: True if the prompt is successfully added, False otherwise.
    """
    hash_id = create_short_hash(prompt, parent_id)
    
    if hash_id in prompts_data["prompts"]:
        return False  # Prompt already exists, do not add

    prompt_record = {
        "text": prompt,
        "metadata": metadata if metadata else {},
        "children": children if children else [],
        "parent": parent_id
    }
    prompts_data["prompts"][hash_id] = prompt_record

    if parent_id and parent_id in prompts_data["prompts"]:
        parent_prompt = prompts_data["prompts"][parent_id]
        parent_prompt["children"].append(hash_id)
        prompts_data["prompts"][parent_id] = parent_prompt

    return True

def verify_prompt_hash(prompts_data, hash_id):
    """
    Verify the integrity of a prompt based on its hash ID.

    Parameters:
    prompts_data (dict): The dictionary containing prompts data.
    hash_id (str): The hash ID of the prompt to verify.

    Returns:
    bool: True if the hash ID is valid and matches the prompt, False otherwise.
    """
    if hash_id not in prompts_data["prompts"]:
        return False  # Prompt not found

    prompt = prompts_data["prompts"][hash_id]
    parent_id = prompt["parent"]
    reconstructed_hash = create_short_hash(prompt["text"], parent_id)

    if reconstructed_hash != hash_id:
        return False  # Hash mismatch

    if not parent_id:
        return True

    return verify_prompt_hash(prompts_data, parent_id)

def clone_and_link_as_child(prompts_data, prompt_id_to_clone, parent_id):
    """
    Clones a prompt and links it as a child to another prompt.

    Parameters:
    prompts_data (dict): The dictionary containing prompts data.
    prompt_id_to_clone (str): The unique hash ID of the prompt to be cloned.
    parent_id (str): The unique hash ID of the parent prompt.

    Returns:
    str: The unique hash ID of the cloned prompt if successful, None otherwise.
    """
    if prompt_id_to_clone in prompts_data["prompts"] and parent_id in prompts_data["prompts"]:
        # Clone the prompt
        original_prompt = prompts_data["prompts"][prompt_id_to_clone]
        new_prompt_text = original_prompt["text"]
        new_metadata = original_prompt.get("metadata", {})

        # Create a new unique hash ID for the cloned prompt
        new_hash_id = create_short_hash(new_prompt_text, parent_id)

        # Check if the new hash ID already exists
        if new_hash_id in prompts_data["prompts"]:
            return None  # Cloned prompt already exists

        # Add the cloned prompt to prompts_data
        cloned_prompt = {
            "text": new_prompt_text,
            "metadata": new_metadata,
            "children": [],
            "parent": parent_id
        }
        prompts_data["prompts"][new_hash_id] = cloned_prompt

        # Link the cloned prompt as a child to the parent prompt
        prompts_data["prompts"][parent_id]["children"].append(new_hash_id)

        return new_hash_id
    else:
        return None  # Either the prompt to clone or the parent prompt does not exist

def update_metadata_by_id(prompts_data, unique_id, new_metadata):
    """
    Update the metadata of a prompt identified by its unique hash ID.

    Parameters:
    prompts_data (dict): The dictionary containing prompts data.
    unique_id (str): The unique hash ID of the prompt to be updated.
    new_metadata (dict): The new metadata to be updated.

    Returns:
    bool: True if the update was successful, False otherwise.
    """
    if unique_id in prompts_data["prompts"]:
        prompts_data["prompts"][unique_id]["metadata"] = new_metadata
        return True
    else:
        return False  # Unique ID not found

def chain_prompts(prompts_data, prompt_chain):
    """
    Chains a list of prompts together, adding each subsequent prompt as a child of the prior prompt.

    Parameters:
    prompts_data (dict): The dictionary containing prompts data.
    prompt_chain (list): A list of prompts to be chained together.

    Returns:
    list: A list of unique hash IDs for the prompts in the chain.
    """
    parent_id = None
    chain_ids = []

    for prompt in prompt_chain:
        # Add each prompt using the add_prompt function
        if add_prompt(prompts_data, prompt["prompt"], parent_id, prompt.get("metadata", {})):
            # Retrieve the hash ID of the newly added prompt
            new_prompt_id = create_short_hash(prompt["prompt"], parent_id)
            chain_ids.append(new_prompt_id)

            # Set the current prompt as the parent for the next one
            parent_id = new_prompt_id
        else:
            print(f"Failed to add or duplicate found for prompt: {prompt['prompt']}")

    return chain_ids
