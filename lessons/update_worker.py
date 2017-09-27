from twilio.rest import Client
import os

# Your Account Sid and Auth Token from twilio.com/user/account
account_sid = os.environ.get("TWILIO_ACME_ACCOUNT_SID")
auth_token = os.environ.get("TWILIO_ACME_AUTH_TOKEN")
workspace_sid = os.environ.get("TWILIO_ACME_WORKSPACE_SID")
worker_sid = "WK7d2e2a04bb9afb289cec096e07221409" #Francisco
support_level ="9"
client = Client(account_sid, auth_token)

worker = client.taskrouter.workspaces(workspace_sid) \
        .workers(worker_sid).fetch()

#update will wipeout current attributes so make sure to either retain or include current attritutes
worker = worker.update(attributes='{"languages": ["en", "fr", "es"],"skills": ["support", "billing", "sales"],"contact_uri": "client: WK7d2e2a04bb9afb289cec096e07221409", "support:"'+ support_level+ '"}')


worker = client.taskrouter.workspaces(workspace_sid) \
                                      .workers(worker_sid).fetch()

print(worker.friendly_name)
print(worker.attributes)

