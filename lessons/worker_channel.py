from twilio.rest import Client
import os

account_sid = os.environ.get("TWILIO_ACME_ACCOUNT_SID")
auth_token = os.environ.get("TWILIO_ACME_AUTH_TOKEN")
workspace_sid = os.environ.get("TWILIO_ACME_WORKSPACE_SID")
workflow_sid = os.environ.get("TWILIO_ACME_SUPPORT_WORKFLOW_SID") #support
workflow_sales_sid = os.environ.get("TWILIO_ACME_SALES_WORKFLOW_SID") #sales
workflow_billing_sid = os.environ.get("TWILIO_ACME_BILLING_WORKFLOW_SID") #billing
workflow_OOO_sid = os.environ.get("TWILIO_ACME_OOO_SID")
worker_sid = "WK7d2e2a04bb9afb289cec096e07221409"

client = Client(account_sid, auth_token)

#print taskchannel for workspace
task_channel = client.taskrouter.workspaces(workspace_sid).task_channels.get('chat').fetch()
print(task_channel.friendly_name)
print(task_channel.sid)

worker_channel = client.taskrouter.workspaces(workspace_sid).workers(worker_sid).worker_channels.list()
for channel in worker_channel:

        print(worker_channel.task_channel_unique_name)
