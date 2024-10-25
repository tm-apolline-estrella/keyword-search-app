# Import standard library modules
import json
import urllib.parse
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

# Import local modules
from src.components.coach_ai.schemas import ChatRequestConversation

base_dir = Path(__file__).parent.parent


def find_last_index(my_list: List[dict], role: str) -> Union[int, None]:
    last_index = None
    for i in range(len(my_list) - 1, -1, -1):
        if my_list[i]["role"] == role:
            last_index = i
            break
    return last_index


def transform_messages(messages: List[Dict[str, str]]) -> List[Tuple[str]]:
    result = []
    temp = []
    for message in messages:
        if message["role"] == "user":
            if temp:
                result.append(tuple(temp))
                temp = []
            temp.append(message["content"])
        else:
            temp.append(message["content"])
    if temp:
        result.append(tuple(temp))
    return result


def get_last_user_message(conversation: ChatRequestConversation) -> Optional[str]:
    last_user_index = find_last_index(conversation, "user")
    if last_user_index is not None:
        last_user_message = conversation.pop(last_user_index)
        return last_user_message["content"]


def format_data(data: Union[str, List[str]]):
    return json.dumps({"data": data})


def get_filename(path: str) -> str:
    return path.split("/")[-1].split(".")[0].replace(" ", "_")


def get_filename_and_page_from_path_list(
    path_list: List[Dict[str, Union[int, str]]]
) -> List[Dict[str, Union[int, str]]]:
    new_source = [
        {"page": doc["page"], "filename": get_filename(doc["source"])}
        for doc in path_list
    ]
    return new_source


def get_date_today():
    return date.today().strftime("%B %d, %Y")


def load_prompt_template(
    filename: str, folder_path: str = str(base_dir / "prompts")
) -> str:
    full_filename = filename + ".txt"
    data = Path(folder_path) / full_filename
    return data.read_text()


def format_source_similarity_search_results(docs) -> List[Dict[str, str]]:
    formatted_docs = []

    for doc in docs:
        new_doc = {
            "filename": get_filename(doc.metadata["source"]),
            "chunks": json.dumps(doc.page_content.split("\n")),
            "dateIngested": doc.metadata["creationDate"],
        }
        source_encoded = urllib.parse.quote(doc.metadata["source"])
        new_doc["link"] = f"{source_encoded}#page={doc.metadata['page']}"
        formatted_docs.append(new_doc)

    return formatted_docs


def extract_email_from_filter(group_id: str) -> str:
    delimeter = ":"
    email = group_id.split(delimeter)[1]
    return email


def lower_user_email_not_domain(email: str) -> List:
    delimeter = "@"
    parts = email.split(delimeter)
    lowercase_username = parts[0].lower()
    domain = parts[1]
    return f"{lowercase_username}@{domain}"


def lowercase_user_roles(group_ids: List[str]):
    new_group_ids = []
    for group_id in group_ids:
        if "User:" in group_id:
            email = extract_email_from_filter(group_id)
            lowercase_email = lower_user_email_not_domain(email)
            new_group_ids.append(f"User:{lowercase_email}")
        else:
            new_group_ids.append(group_id)
    return new_group_ids
