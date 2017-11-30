from twilio.rest import Client
from time import sleep

# Your Account Sid and Auth Token from twilio.com/user/account
account_sid = ""
auth_token = ""
client = Client(account_sid, auth_token)

call = client.calls("CAa23c6fbd3a0a85f9b975e6e5c1c8bbab").fetch()
print(call.sid)
print(call.answered_by)
