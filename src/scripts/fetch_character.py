import argparse
import re
from typing import Optional

import requests

HOST_NAME = "https://www.pathofexile.com/"
PROFILE_PATH = "account/view-profile/"
CHARACTER_PATH = "character-window/get-characters"
PASSIVE_TREE_PATH = "character-window/get-passive-skills"
ITEM_PATH = "character-window/get-items"

realms = {
    "pc": {
        "realmCode": "pc",
        "hostName": "https://www.pathofexile.com/",
        "profileURL": "account/view-profile/",
    },
    "xbox": {
        "realmCode": "xbox",
        "hostName": "https://www.pathofexile.com/",
        "profileURL": "account/xbox/view-profile/",
    },
    "sony": {
        "realmCode": "sony",
        "hostName": "https://www.pathofexile.com/",
        "profileURL": "account/sony/view-profile/",
    },
    "garena": {
        "realmCode": "pc",
        "hostName": "https://web.poe.garena.tw/",
        "profileURL": "account/view-profile/",
    },
    "tencent": {
        "realmCode": "pc",
        "hostName": "https://poe.game.qq.com/",
        "profileURL": "account/view-profile/",
    },
}
realm_code = "pc"
headers = {"User-Agent": "Path of Building Community", "Accept": ""}


def import_characters(account_name: str) -> Optional[tuple[str, dict]]:
    url = f"{HOST_NAME}{CHARACTER_PATH}"
    params = {"accountName": account_name, "realm": realm_code}
    try:
        response = requests.get(url, params=params, headers=headers, timeout=6.0)
    except requests.RequestException as e:
        print(f"Error retrieving account: {e}.")
        return
    characters = response.json()
    url = f"{HOST_NAME}{PROFILE_PATH}{account_name}"
    try:
        response = requests.get(url, headers=headers, timeout=6.0)
    except requests.RequestException as e:
        print(f"Error retrieving character list: {e}.")
        return
    if m := re.search(r"/view-profile/(\w+)/characters", response.text):
        return m.group(1), characters


def import_passive_tree(account_name: str, char_name: str) -> Optional[dict]:
    url = f"{HOST_NAME}{PASSIVE_TREE_PATH}"
    params = {"accountName": account_name, "character": char_name, "realm": realm_code}
    try:
        response = requests.get(url, params=params, headers=headers, timeout=6.0)
    except requests.RequestException as e:
        print(f"Error retrieving passive skill tree: {e}.")
        return
    return response.json()


def import_items(account_name: str, char_name: str) -> Optional[dict]:
    url = f"{HOST_NAME}{ITEM_PATH}"
    params = {"accountName": account_name, "character": char_name, "realm": realm_code}
    try:
        response = requests.get(url, params=params, headers=headers, timeout=6.0)
    except requests.RequestException as e:
        print(f"Error retrieving items: {e}.")
        return
    return response.json()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse Character/Account Info")
    parser.add_argument("account_name", help="account name", type=str)
    parser.add_argument("--realm", help="specify realm code (e.g., pc, xbox, sony)")
    args = parser.parse_args()
    print(args)
    if args.realm:
        try:
            realm_code = realms[args.realm.lower()]["realmCode"]
            HOST_NAME = realms[args.realm.lower()]["hostName"]
            PROFILE_PATH = realms[args.realm.lower()]["profileURL"]
        except KeyError:
            pass
    current_league = "Standard"
    name, characters = import_characters(args.account_name)
    if characters and "error" not in characters:
        current_league_characters = [
            character["name"]
            for character in characters
            if character["league"] == current_league
        ]
        print(f"[{current_league.upper()}] Characters: {current_league_characters}")
        passive_tree = import_passive_tree(name, current_league_characters[0])
        items = import_items(name, current_league_characters[0])
