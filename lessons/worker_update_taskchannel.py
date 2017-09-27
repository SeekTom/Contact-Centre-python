from twilio.rest import Client
import os

account_sid = os.environ.get("TWILIO_ACME_ACCOUNT_SID")
auth_token = os.environ.get("TWILIO_ACME_AUTH_TOKEN")
workspace_sid = os.environ.get("TWILIO_ACME_WORKSPACE_SID")
workflow_sid = os.environ.get("TWILIO_ACME_SUPPORT_WORKFLOW_SID") #support
workflow_sales_sid = os.environ.get("TWILIO_ACME_SALES_WORKFLOW_SID") #sales
workflow_billing_sid = os.environ.get("TWILIO_ACME_BILLING_WORKFLOW_SID") #billing
workflow_OOO_sid = os.environ.get("TWILIO_ACME_OOO_SID")

client = Client(account_sid, auth_token)
worker_channel = client.taskrouter.workspaces(workspace_sid) \
    .workers("WK376dcd75a6d58f2cce742302a0e79862").worker_channels('TC1e171fc73ce4b850fd96bed0012c0fd2').fetch
#taskqueue = taskqueue.update(target_workers='languages HAS "english"')

print(worker_channel)