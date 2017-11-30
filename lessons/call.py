# Download the Python helper library from twilio.com/docs/python/install
from twilio.rest import Client
from time import sleep

# Your Account Sid and Auth Token from twilio.com/user/account
account_sid = ""
auth_token = ""
client = Client(account_sid, auth_token)

call = client.calls.create(
    to="+447737088306",
    from_="+441163260745",
    machine_detection="Enable",
    method="GET",
    status_callback="https://requestb.in/1jigllq1",
    url="http://twimlbin.com/59b6d602"
)

print(call.sid)
print(call.answered_by)
sleep(6)
call2 = client.calls(call.sid).fetch()
print(call2.to)
print(call2.answered_by)