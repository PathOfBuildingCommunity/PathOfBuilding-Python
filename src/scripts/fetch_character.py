import json
import re
from typing import Optional

import requests

HOST_NAME = "https://www.pathofexile.com/"
CHARACTER_PATH = "character-window/get-characters"
PROFILE_PATH = "account/view-profile/"
PASSIVE_TREE_PATH = "character-window/get-passive-skills"

headers = {"User-Agent": "Path of Building Community", "Accept": ""}
realm_code = "pc"


def import_characters(account_name: str) -> Optional[tuple[str, dict]]:
    url = f"{HOST_NAME}{CHARACTER_PATH}"
    params = {"accountName": account_name, "realm": realm_code}
    try:
        response = requests.get(url, params=params, headers=headers, timeout=6.0)
    except requests.RequestException as e:
        print(f"Error retrieving account: {e}.")
        return
    print(response.url)
    characters = response.json()
    print(f"Character list:\n{json.dumps(characters, indent=4)}")
    url = f"{HOST_NAME}{PROFILE_PATH}{account_name}"
    try:
        response = requests.get(url, headers=headers, timeout=6.0)
    except requests.RequestException as e:
        print(f"Error retrieving character list: {e}.")
        return
    if m := re.search(r"/view-profile/(\w+)/characters", response.text):
        return m.group(1), characters


def import_passive_tree(account_name: str, char_name: str):
    url = f"{HOST_NAME}{PASSIVE_TREE_PATH}"
    params = {"accountName": account_name, "character": char_name, "realm": realm_code}
    try:
        response = requests.get(url, params=params, headers=headers, timeout=6.0)
    except requests.RequestException as e:
        print(f"Error retrieving passive skill tree: {e}.")
        return
    passive_tree = response.json()
    print(f"Tree:\n{json.dumps(passive_tree, indent=4)}")


if __name__ == "__main__":
    player_name = "GlobalIdentity"
    player_name, player_characters = import_characters(player_name)
    leagues = [c["name"] for c in player_characters if c["league"] == "Ritual"]
    print(leagues)
    import_passive_tree(player_name, leagues[1])
