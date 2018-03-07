# Contact-Centre Version 0.5

Inbound PSTN to Twilio Client Contact Centre Powered by Taskrouter 

Languages: Python, js

This implements:

- Two channels (Voice & Programmable Chat)
- 4 department, multilingual contact centre
- Agent UI based on TaskRouter SDK for low latency
- Twilio Client WebRTC dashboard
- Conference instruction
- Call instruction
- Conference recording
- Call holding
- Call transfers
- Programmable Chat
- Multitasking

Install the requirements by running `pip install requirements.txt`
Run the install script to create the basic contact center structure

## Setup
1. Setup a new TwiML App https://www.twilio.com/console/voice/twiml/apps and point it to the domain where you deployed this app (add `/incoming_call` suffix): `https://YOUR_DOMAIN_HERE/incoming_call`
2. Buy a Twilio number https://www.twilio.com/console/phone-numbers/incoming
3. Configure your number to point towards this TwiML App (Voice: Configure With: TwiML App)
4. Define the following env variables:
```
TWILIO_ACME_ACCOUNT_SID - your Account SID
TWILIO_ACME_AUTH_TOKEN - your Auth Token

TWILIO_ACME_TWIML_APP_SID - SID of the TwiML App created in point 1. above
TWILIO_ACME_CALLERID - phone number bought in point 2. above (in E.164 format, e.g. '+1xxxxxxxxxx')

TWILIO_ACME_WORKSPACE_SID - TaskRouter Workspace the application should use
TWILIO_ACME_SUPPORT_WORKFLOW_SID - Support WorkFlow SID
TWILIO_ACME_MANAGER_WORKFLOW_SID - Manager WorkFlow SID
```