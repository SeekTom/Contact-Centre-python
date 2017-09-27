
from twilio.twiml.voice_response import VoiceResponse, Enqueue
import os

account_sid = os.environ.get("TWILIO_ACME_ACCOUNT_SID")
auth_token = os.environ.get("TWILIO_ACME_AUTH_TOKEN")
workspace_sid = os.environ.get("TWILIO_ACME_WORKSPACE_SID")
workflow_sid = os.environ.get("TWILIO_ACME_SUPPORT_WORKFLOW_SID")

resp = VoiceResponse()

with resp.enqueue(None, workflowSid=workflow_sid) as e:
    e.task('{"selected_language" : "es", "Selected_department" : "test"}')
print(resp)
print("cheese")