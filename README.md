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

You will need to add in your own:

- AccountSID,
- AuthToken,
- Twiml ApplicationSID,
- WorkspaceSid
- WorkflowSids (Sales, Support, Billing, Managers, OOO)

You will need to configure the above workspaces, workflows, taskqueues and assorted workers via the TaskRouter Console

Configure your number to point towards https://YOUR_DOMAIN_HERE/incoming_call

