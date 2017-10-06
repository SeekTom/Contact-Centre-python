from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Enqueue
import os

workflow_sid = os.environ.get("TWILIO_ACME_SUPPORT_WORKFLOW_SID")

resp = VoiceResponse()

with resp.enqueue(None, workflowSid=workflow_sid) as e:
    e.task('{"selected_language" : "es", "Selected_department" : "test"}')
print(resp)

