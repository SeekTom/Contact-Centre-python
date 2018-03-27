# Contact-Centre Version 0.5

Inbound PSTN to Twilio Client Contact Centre Powered by Taskrouter 

Languages: Python, js

This implements:

- Single channel (Voice)
- 4 department, multilingual contact centre
- Agent UI based on TaskRouter SDK for low latency
- Twilio Client WebRTC dashboard
- Conference instruction
- Call instruction
- Conference recording
- Call holding
- Call transfers


Install the requirements by running `pip install requirements.txt`
Run the install script to create the basic contact center structure

## Setup
1. Setup a new TwiML App https://www.twilio.com/console/voice/twiml/apps and point it to the domain where you deployed this app (add `/incoming_call` suffix): `https://YOUR_DOMAIN_HERE/incoming_call`
2. Buy a Twilio number https://www.twilio.com/console/phone-numbers/incoming
3. Configure your number to point towards this TwiML App (Voice: Configure With: TwiML App)
4. Define the following env variables:

```
account_sid = os.environ.get("TWILIO_ACME_ACCOUNT_SID")
auth_token = os.environ.get("TWILIO_ACME_AUTH_TOKEN")
workspace_sid = os.environ.get("TWILIO_ACME_WORKSPACE_SID") # workspace
workflow_support_sid = os.environ.get("TWILIO_ACME_SUPPORT_WORKFLOW_SID")  # support workflow
workflow_sales_sid = os.environ.get("TWILIO_ACME_SALES_WORKFLOW_SID")  # sales workflow
workflow_billing_sid = os.environ.get("TWILIO_ACME_BILLING_WORKFLOW_SID")  # billing workflow
workflow_mngr_sid = os.environ.get("TWILIO_ACME_MANAGER_WORKFLOW_SID") # manager escalation workfloq
twiml_app = os.environ.get("TWILIO_ACME_TWIML_APP_SID") # Twilio client application SID
caller_id = os.environ.get("TWILIO_ACME_CALLERID") # Contact Center's phone number to be used in outbound communication

```