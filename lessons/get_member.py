from twilio.rest import Client
import os

# Your Account Sid and Auth Token from twilio.com/user/account
account = os.environ.get("TWILIO_ACME_ACCOUNT_SID")
token = os.environ.get("TWILIO_ACME_AUTH_TOKEN")
chat_service = os.environ.get("TWILIO_ACME_CHAT_SERVICE_SID")

client = Client(account, token)

member = client.chat \
               .services(chat_service) \
               .channels("CHbaa0d16b33944ef9bce5a69dd3a8dfc8") \
               .members("Francisco") \
               .fetch()

print(member.sid)