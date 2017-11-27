# Download the Python helper library from twilio.com/docs/python/install
from twilio.rest import Client
import os

# Your Account Sid and Auth Token from twilio.com/user/account
account_sid = os.environ.get("TWILIO_ACME_ACCOUNT_SID")
auth_token = os.environ.get("TWILIO_ACME_AUTH_TOKEN")
workspace_sid = os.environ.get("TWILIO_ACME_WORKSPACE_SID")
taskqueue_sid = "WQ62f64e2c6ab763b97cd9e9c142aeec33"
client = Client(account_sid, auth_token)
events = client.taskrouter.workspaces(workspace_sid) \
                                  .events.list()

for event in events:
    print(event.event_type)
else:
    print("nothing found")


statistics = client.taskrouter.workspaces(workspace_sid) \
   .task_queues(taskqueue_sid).statistics().fetch()

print(statistics)