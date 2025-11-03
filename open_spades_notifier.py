import json
import subprocess
from time import sleep
import requests
from requests.exceptions import RequestException


"""
Example server data structure:
{
  'country': 'US',
  'game_mode': 'babel',
  'game_version': '0.75',
  'identifier': 'aos://3782433610:32000',
  'last_updated': 1762181693,
  'latency': 104,
  'map': 'nightmare',
  'name': 'aloha.pk tower of babel',
  'players_current': 10,
  'players_max': 32
}
"""


# --- Configuration Constants ---
URL = "http://services.buildandshoot.com/serverlist.json"
TARGET_SERVER_NAME = "aloha.pk tower of babel"
CHECK_INTERVAL_SECONDS = 60 * 1  # Wait 2 minutes between checks
FAVORITE_MAPS = []  # List of map names you like


def filter_by_server(server_name, server_list):
    """
    Find the first server in the list matching the given name.

    :param server_name: The name of the server to search for.
    :param server_list: A list of server dictionaries.
    :return: The matching server dictionary, or None if not found.
    """
    for item in server_list:
        if item.get("name") == server_name:
            return item
    return None


def load_server_list(url=URL):
    """Loads the JSON server list from the given URL."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        print(f"ERROR: Failed to load server list from {url}: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"ERROR: Failed to decode JSON data: {e}")
        return None


def send_notification(title, message, icon="dialog-information"):
    """
    Sends a desktop notification on Linux using notify-send.

    :param title: Notification title.
    :param message: Notification body text.
    :param icon: Optional system icon name.
    """
    try:
        subprocess.run(
            ["notify-send", title, message, "-i", icon],
            check=True,
        )
    except FileNotFoundError:
        print("ERROR: 'notify-send' not found. Install 'libnotify-bin'.")
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to send notification: {e}")


def main():
    last_map = None

    while True:
        server_list = load_server_list(URL)
        if server_list is None:
            print("ERROR: Server list is None.")
            sleep(CHECK_INTERVAL_SECONDS)
            continue

        server_data = filter_by_server(TARGET_SERVER_NAME, server_list)
        if server_data is None:
            print("ERROR: Target server not found.")
            sleep(CHECK_INTERVAL_SECONDS)
            continue

        current_map = server_data["map"]
        current_players = server_data["players_current"]
        players_max = server_data["players_max"]


        if last_map is None:
            # 1.) no current map
            last_map = current_map
            print(f"New map: {current_map} ({current_players:2d}/{players_max:2d})")
            send_notification(
                "OpenSpades: New Map!",
                f"New map: {current_map} ({current_players:2d}/{players_max:2d})",
                icon="terminal",
            )
            
        elif last_map == current_map:
            # 2.) No change
            print(f"{current_map} ({current_players:2d}/{players_max:2d})")

        elif last_map != current_map and current_map in FAVORITE_MAPS:
            # 3.) New map is your favourite!
            last_map = current_map
            print(f"New map: {current_map} ({current_players:2d}/{players_max:2d})")
            send_notification(
                "OpenSpades: New Map is your favorite!!!",
                f"New map: {current_map} ({current_players:2d}/{players_max:2d})",
                icon="emblem-favorite",
            )

        elif last_map != current_map:
            # 4.) New map!
            last_map = current_map
            print(f"New map: {current_map} ({current_players:2d}/{players_max:2d})")
            send_notification(
                "OpenSpades: New Map!",
                f"New map: {current_map} ({current_players:2d}/{players_max:2d})",
                icon="terminal",
            )

        sleep(CHECK_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
