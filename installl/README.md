#Contact center setup script

This script will setup a demo TaskRouter instance

- A workspace
- Five Workers with attributes
- Five TaskQueues 
- One Workflow

usage: taskrouter_cli.py [-h] [-d] [-l] [-i] [--sid WS_SID] [--name WS_NAME]
                         [--url WS_URL]

Twilio TaskRouter Console Manager

optional arguments:
  -h, --help      show this help message and exit
  -d, --delete    Delete Workspace and all of its content
  -l, --list      List existing Workspaces
  -i, --init      Initialize new Workspace
  --sid WS_SID    Workspace SID
  --name WS_NAME  Workspace Name
  --url WS_URL    Event Callback URL

