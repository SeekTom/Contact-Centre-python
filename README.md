# Contact-Centre

Inbound PSTN to Twilio Client Contact Centre Powered by Taskrouter version 0.3

Languages: Python, js

This implements:

- 4 channel, multilingual contact centre
- Agent UI based on TaskRouter SDK for low latency
- Working hours
- Agent Conference
- Conference recording
- Conference statuscallback monitoring

You will need to add in your own:

- AccountSID,
- AuthToken,
- Twiml ApplicationSID,
- WorkspaceSid
- WorkflowSids (Sales, Support, Billing, Managers, OOO)

You will need to configure the above workspaces, workflows, taskqueues and assorted workers via the TaskRouter Console

Configure your number to point towards https://YOUR_DOMAIN_HERE/incoming_call

