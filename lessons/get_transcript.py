from twilio.rest import Client
import os

# Initialize the client
account = os.environ.get("TWILIO_ACME_ACCOUNT_SID")
token = os.environ.get("TWILIO_ACME_AUTH_TOKEN")
chat_service = os.environ.get("TWILIO_ACME_CHAT_SERVICE_SID")


client = Client(account, token)

messages = client.chat \
                .services(chat_service) \
                .channels("CH1cfc90f587304eafb7af60199aceb635") \
                .messages \
                .list()

for message in messages:
    print(message.from_ + ": " + message.body)