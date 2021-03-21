from urllib.parse import urlencode
from urllib.request import Request, urlopen
import json
import pathlib
import confply.log as log


uploads = []
bot_token = None

failure_str = """
:red_circle: {project_str} `{config_path}` was a failure! :red_circle:
You touched it last, {user}

```
{vcs_log}
```
"""
success_str = """
:large_green_circle: {project_str} `{config_path}` was a success! :large_green_circle:
"""

class api():
    user_list = "https://slack.com/api/users.list"
    channel_list = "https://slack.com/api/conversations.list"
    member_list = "https://slack.com/api/conversations.members"
    chat_post = "https://slack.com/api/chat.postMessage"
    files_upload = "https://slack.com/api/files.upload"


def send_report(report):
    report["project_str"] = (pathlib.Path(report["vcs_root"]).name)
    if report["status"] == "success":
        message = success_str
    else:
        message = failure_str

    for key, val in report.items():
        message = message.replace("{"+key+"}", str(val))

    send_message(message=message, user=report["vcs_author"], files=uploads)


def send_message(message="hello from confply, {user}", user=None, files=[]):
    payload = {"token": bot_token}
    request = Request(api.user_list, urlencode(payload).encode())
    response = urlopen(request).read().decode()
    response = json.loads(response)
    user_id = None
    confply_id = None

    for mem in response["members"]:
        if user in mem["name"]:
            user_id = mem["id"]
        elif user in mem["real_name"]:
            user_id = mem["id"]
        elif "confply" == mem["name"] and mem["is_bot"]:
            confply_id = mem["id"]

    request = Request(api.channel_list, urlencode(payload).encode())
    response = urlopen(request).read().decode()
    response = json.loads(response)
    channel_ids = []
    for channel in response["channels"]:
        channel_ids.append(channel["id"])

    valid_channels = []
    for channel_id in channel_ids:
        payload["channel"] = channel_id
        request = Request(api.member_list, urlencode(payload).encode())
        response = urlopen(request).read().decode()
        response = json.loads(response)
        if user_id is not None:
            if (response["ok"] and
                    user_id in response["members"] and
                    confply_id in response["members"]):
                valid_channels.append(channel_id)
        else:
            valid_channels.append(channel_id)

    for channel in valid_channels:
        payload["channel"] = channel
        payload["text"] = message.replace("{user}", "<@"+user_id+">")
        request = Request(api.chat_post, urlencode(payload).encode())
        response = urlopen(request).read().decode()
        response = json.loads(response)
        for upload_file in files:
            path = pathlib.Path(upload_file)
            if path.exists():
                del payload["text"]
                with open(upload_file) as file_str:
                    
                    payload["title"] = path.name
                    payload["content"] = file_str.read()
                    payload["channels"] = channel
                    payload["thread_ts"] = response["ts"]
                    request = Request(api.files_upload, urlencode(payload).encode())
                    response = urlopen(request).read().decode()
                    response = json.loads(response)
            else:
                log.warning("couldn't find "+path.absolute())
    pass
