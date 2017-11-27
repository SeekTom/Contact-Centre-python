from twilio.rest import Client
import os

account_sid = os.environ.get("ACME_ACCOUNT_SID")
auth_token = os.environ.get("ACME_AUTH_TOKEN")
client = Client(account_sid, auth_token)

print("Welcome to the TaskRouter creator!")
workspace_name = input("Please enter a name for your Workspace")
#create workspace

workspace = client.taskrouter.v1.workspaces.create(friendly_name=workspace_name, event_callback_url='https://requestb.in/y4r0axy4?inspect', template='FIFO')
workspace_sid =  workspace.Sid

print("Workspace " + workspace_name + "created, sid: " + workspace_sid)
taskqueue_name = input("Please enter a name for your taskqueue")
print(workspace.activities.list())


taskqueue = workspace.task_queues.create(taskqueue_name)

#create a TaskQueue

print

