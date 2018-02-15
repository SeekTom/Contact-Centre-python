**Contact center setup script**

This script will setup a demo TaskRouter instance

- A workspace
- Five Workers with attributes
- Five TaskQueues 
- One Workflow

**Usage:**

- Add your accountSID and AuthToken on lines 8 & 9:
-- account_sid = os.environ.get("TWILIO_ACME_ACCOUNT_SID")
- auth_token = os.environ.get("TWILIO_ACME_AUTH_TOKEN")

If you wanted to create a new workspace with the Friendly name of MyNewWorkSpace:

`python taskrouter_cli.py --name MyNewWorkSpace`

**Twilio TaskRouter Console Manager**

taskrouter_cli.py [-h] [-d] [-l] [-i] [--sid WS_SID] [--name WS_NAME]
                         [--url WS_URL]
optional arguments:
  -h, --help      show this help message and exit
  -d, --delete    Delete Workspace and all of its content
  -l, --list      List existing Workspaces
  -i, --init      Initialize new Workspace
  --sid WS_SID    Workspace SID
  --name WS_NAME  Workspace Name
  --url WS_URL    Event Callback URL

