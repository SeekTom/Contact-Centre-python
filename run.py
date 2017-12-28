from flask import Flask, request, Response, render_template, jsonify
from twilio.rest import Client
from twilio.jwt.taskrouter.capabilities import WorkerCapabilityToken
from twilio.twiml.voice_response import VoiceResponse, Conference, Enqueue, Dial
from twilio.twiml.messaging_response import Message, MessagingResponse
from twilio.jwt.client import ClientCapabilityToken
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import (ChatGrant)

import os

app = Flask(__name__, static_folder='app/static')

# Your Account Sid and Auth Token from twilio.com/user/account
account_sid = os.environ.get("TWILIO_ACME_ACCOUNT_SID")
auth_token = os.environ.get("TWILIO_ACME_AUTH_TOKEN")

workspace_sid = os.environ.get("TWILIO_ACME_WORKSPACE_SID")
workflow_sid = os.environ.get("TWILIO_ACME_SUPPORT_WORKFLOW_SID")  # support
workflow_sales_sid = os.environ.get("TWILIO_ACME_SALES_WORKFLOW_SID")  # sales
workflow_billing_sid = os.environ.get("TWILIO_ACME_BILLING_WORKFLOW_SID")  # billing
workflow_OOO_sid = os.environ.get("TWILIO_ACME_OOO_SID")

api_key = os.environ.get("TWILIO_ACME_CHAT_API_KEY")
api_secret = os.environ.get("TWILIO_ACME_CHAT_SECRET")
chat_service = os.environ.get("TWILIO_ACME_CHAT_SERVICE_SID")


twiml_app = os.environ.get("TWILIO_ACME_TWIML_APP_SID")
caller_id = os.environ.get("TWILIO_ACME_CALLERID")

client = Client(account_sid, auth_token)


# private functions

def return_work_space(digits):

    #query user input and assign the correct workspace

    digit_pressed = digits
    if digit_pressed == "1":
        department = "sales"
        work_flow_sid = workflow_sales_sid
        workflowdata = (work_flow_sid, department)  # tuple

        return workflowdata

    if digit_pressed == "2":
        department = "support"
        work_flow_sid = workflow_sid
        workflowdata = (work_flow_sid, department) # tuple

        return workflowdata

    if digit_pressed == "3":
        department = "billing"
        work_flow_sid = workflow_billing_sid
        workflowdata = (work_flow_sid, department) # tuple

        return workflowdata


# Render index

@app.route("/", methods=['GET', 'POST'])
def hello_world():
    return render_template('index.html')


# Default route for support line voice request url
#Gather to select language

@app.route("/incoming_call", methods=['GET', 'POST'])
def incoming_call():
    resp = VoiceResponse()
    with resp.gather(num_digits="1", action="/incoming_call/department", timeout=10) as g:
        g.say("Para Espanol oprime el uno.", language='es')
        g.say("For English, press two.", language='en')
        g.say("Pour Francais, pressé un", language='fr')

    return Response(str(resp), mimetype='text/xml')


##################################################################

#redirect the user to the correct department for their language choice

@app.route("/incoming_call/department", methods=['POST', 'GET'])
def choose_dept():
    resp = VoiceResponse()
    if 'Digits' in request.values:
        # Get which digit the caller chose
        choice = int(request.values['Digits'])
        switcher = {
          1: "es",
          2: "en",
          3: "fr"
        }
        dept_lang = switcher.get(choice)
        resp.redirect("/dept?lang="+dept_lang+"&digit="+str(choice))
        return str(resp)


# Select department

@app.route("/dept", methods=['GET', 'POST'])
def dept():
    resp = VoiceResponse()
    dept_lang = request.values['lang']
    digit = request.values['digit']
    say_dict = {
      'es': ["Para sales oprime uno", "Para support oprime duo", "para billing oprime tres"],
      'en': ["For Sales press one", "For Support press two", "For Billing press three"],
      'fr': ["Pour sales pressé un", "Pour support pressé deux", "Pour billing pressé tres"]
    }
    with resp.gather(num_digits=digit, action="/enqueue_call?lang="+dept_lang, timeout="10") as g:
        g.say(say_dict.get(dept_lang)[0], language=dept_lang)
        g.say(say_dict.get(dept_lang)[1], language=dept_lang)
        g.say(say_dict.get(dept_lang)[2], language=dept_lang)
    return str(resp)

# Enqueue calls to tasks based on language
#Consider refactoring into single function - DONE

@app.route("/enqueue_call", methods=["GET", "POST"])
def enqueue_call():
    if 'Digits' in request.values:
        digit_pressed = request.values['Digits']
        workflow_d = return_work_space(digit_pressed) #array of workspace and product
        resp = VoiceResponse()
        select_lang = request.values['lang']
        with resp.enqueue(None, workflow_Sid=workflow_d[0]) as e:
            e.task('{"selected_language" : "'+select_lang+'", "selected_product" : "' + workflow_d[1] + '"}')
        return Response(str(resp), mimetype='text/xml')
    else:
        resp = VoiceResponse()
        resp.say("no digits detected") #tell user something is amiss
        resp.redirect("/incoming_call")  #redirect back to initial step
    return Response(str(resp), mimetype='text/xml')


@app.route('/incoming_call', methods=['POST', 'GET'])
def call():
    resp = VoiceResponse()
    with resp.dial(callerId=caller_id) as r:
        r.client('TomPY')
    return str(resp)


###########Agent views ######################

@app.route("/agent_list", methods=['GET', 'POST'])
def generate_agent_list_view():
    # Create arrays of workers and share that with the template so that workers can be queried on the client side

    # All workers can do voice
    all_workers = client.taskrouter.workspaces(workspace_sid).workers.list()

    # Only some workers can do chat
    expression = "skills HAS 'chat'"
    chat_workers = client.taskrouter.workspaces(workspace_sid) \
        .workers.list(target_workers_expression=expression)

    return render_template('agent_list.html', voice_workers=all_workers, chat_workers=chat_workers)


@app.route("/agents", methods=['GET'])
def generate_view(charset='utf-8'):
    # Agent desktop with Twilio Client
    worker_sid = request.args.get('WorkerSid')  # TaskRouter Worker Token
    worker_capability = WorkerCapabilityToken(
        account_sid=account_sid,
        auth_token=auth_token,
        workspace_sid=workspace_sid,
        worker_sid=worker_sid
    )  # generate worker capability token

    worker_capability.allow_update_activities()  # allow agent to update their activity status e.g. go offline
    worker_capability.allow_update_reservations()  # allow agents to update reservations e.g. accept/reject
    worker_token = worker_capability.to_jwt(ttl=28800)

    capability = ClientCapabilityToken(account_sid, auth_token)  # agent Twilio Client capability token
    capability.allow_client_outgoing(twiml_app)
    capability.allow_client_incoming(worker_sid)

    client_token = capability.to_jwt()

    return render_template('agent_desktop.html', token=client_token.decode("utf-8"),
                           worker_token=worker_token.decode("utf-8"),
                           client_name=worker_sid)  # render client/worker tokens to the agent desktop so that they can be queried on the client side


@app.route("/agents/noclient", methods=['GET', 'POST'])
def noClientView():
    # Agent desktop without Twilio Client
    worker_sid = request.args.get('WorkerSid')  # TaskRouter Worker Token
    worker_capability = WorkerCapabilityToken(
        account_sid=account_sid,
        auth_token=auth_token,
        workspace_sid=workspace_sid,
        worker_sid=worker_sid
    )  # generate worker capability token

    worker_capability.allow_update_activities()  # allow agent to update their activity status e.g. go offline
    worker_capability.allow_update_reservations()  # allow agents to update reservations e.g. accept/reject

    worker_token = worker_capability.to_jwt(ttl=28800)

    return render_template('agent_desktop_no_client.html.html', worker_token=worker_token.decode(
        "utf-8"))  # render worker token to the agent desktop so that they can be queried on the client side


# Callbacks

@app.route("/conference_callback", methods=['GET', 'POST'])
def handle_callback():
    #monitor for when the customer leaves a conference and output something to the console
    if 'StatusCallbackEvent' in request.values:

        cb_event = request.values.get('StatusCallbackEvent')
        conf_moderator = request.values.get('StartConferenceOnEnter')
        call = client.calls(request.values.get("CallSid")).fetch()
        caller = call.from_

        if cb_event == "participant-leave":
            if conf_moderator == "true":
                message = client.messages.create(
                    to=caller,
                    from_="+447481343625",
                    body="Thanks for calling OwlCorp, how satisfied were you with your designated agent on a scale of 1 to 10?")
            else:
                print("Something else happened: " + cb_event)
    return render_template('status.html')




@app.route("/callTransfer", methods=['GET', 'POST'])
def transferCall():
    # transfer call
    # put the customer call on hold

    participant = client \
        .conferences(request.values.get('conference')) \
        .participants(request.values.get('participant')) \
        .update(hold=True)
    # create new task for the manager escalation
    # manager workflow is set manually for now, scope for making that a variable based on who the worker is selecting to escalate to in the next version
    # add new attributes on the task for customer callsid, customer tasksid and conference

    task = client.taskrouter.workspaces(workspace_sid).tasks \
        .create(workflow_sid="WW4af8717df650b33eaaf1b9e5f52d8014",
                attributes='{"selected_product":"manager", "conference":"' + request.values.get(
                    'conference') + '", "customer":"' + request.values.get(
                    "customer") + '", "customer_taskSid":"' + request.values.get('taskSid') + '"}')

    resp = VoiceResponse
    return Response(str(resp), mimetype='text/xml')


@app.route("/callmute", methods=['GET', 'POST'])
def unmuteCall():
    # put the customer call on hold
    # grab the conferenceSid and customerCallSid from the values sent by the agent UI

    participant = client \
        .conferences(request.values.get('conference')) \
        .participants(request.values.get('participant')) \
        .update(hold=request.values.get('muted'))

    resp = VoiceResponse
    return Response(str(resp), mimetype='text/xml')


@app.route("/transferTwiml", methods=['GET', 'POST'])
def transferToManager():
    #create TwiML that dials the customer conference add the manager in as a participant

    response = VoiceResponse()
    dial = Dial()

    dial.conference(request.values.get('conference'))

    response.append(dial)

    return Response(str(response), mimetype='text/xml')

@app.route('/chat/')
def chat():

    return render_template('chat.html')

@app.route('/createCustomerChannel', methods=['POST, GET'])
def createCustomerChannel():

    channel = request.values.get('taskSid')

    return channel


@app.route('/createChatTask/', methods=['POST', 'GET'])
def createChatTask():

    task = client.taskrouter.workspaces(workspace_sid).tasks \
        .create(workflow_sid="WW5bc2a216556a9cc2e8d4b8507e8fc502", task_channel="chat",
                attributes='{"selected_product":"chat", "channel":"'+ request.values.get("channel") +'"}')
    task_sid = {"TaskSid": task.sid}
    return jsonify(task_sid)


@app.route('/agent_chat')
def agentChat():
    worker_sid = request.args.get('WorkerSid')  # TaskRouter Worker Token
    worker_capability = WorkerCapabilityToken(
        account_sid=account_sid,
        auth_token=auth_token,
        workspace_sid=workspace_sid,
        worker_sid=worker_sid
    )  # generate worker capability token

    worker_capability.allow_update_activities()  # allow agent to update their activity status e.g. go offline
    worker_capability.allow_update_reservations()  # allow agents to update reservations e.g. accept/reject

    worker_token = worker_capability.to_jwt(ttl=28800)

    return render_template('agent_desktop_chat.html', worker_token=worker_token.decode(
        "utf-8"))
@app.route('/escalateChat/', methods=['POST'])
def escalateChat():

    task = client.taskrouter.workspaces(workspace_sid).tasks \
        .create(workflow_sid="WW4af8717df650b33eaaf1b9e5f52d8014", task_channel="chat",
                attributes='{"selected_product":"manager", "escalation_type": "chat", "channel":"' + request.values.get("channel") + '"}')
    print("Escalation to manager created " + task.sid)
    task_sid = {"TaskSid": task.sid}

    return jsonify(task_sid)

@app.route('/postChat/', methods=['GET'])
def returnTranscript(charset='utf-8'):
    messages = []
    get_transcript = client.chat \
        .services(chat_service) \
        .channels("CHfbb449d4e45840a08c6dbf3bb1cf392d") \
        .messages \
        .list()

    for message in get_transcript:

        messages.append(message.from_ + ": " + message.body)
        print(message.from_ + ": " + message.body)

    data = []

    for messages in get_transcript:

        item = {"message": message.from_ + ": " + message.body}
        data.append(item)

    return render_template('chat_transcript.html', chat_messages=data)


@app.route('/postChat/', methods=['POST'])
def getTranscript():
    #output chat transcript to console
    print(chat_service)
    channel = request.values.get("channel")
    identity = request.values.get("identity")
    messages = []
    # leave channel


    response = client.chat \
        .services(chat_service) \
        .channels(channel) \
        .members(identity) \
        .delete()

    #update channel to state user has left

    leave_message = client.chat \
        .services(chat_service) \
        .channels(channel) \
        .messages \
        .create(identity + " has left the chat.")

    get_transcript = client.chat \
        .services(chat_service) \
        .channels(channel) \
        .messages \
        .list()

    for message in get_transcript:

        messages.append(message.from_ + ": " + message.body)
        print(message.from_ + ": " + message.body)

    return render_template('chat_transcript.html')
    #delete channel

   # response = client.chat \
   #     .services(chat_service) \
    #    .channels(request.values.get("channel")) \
   #     .delete()
  #  return response
# Basic health check - check environment variables have been configured
# correctly
@app.route('/config')
def config():
    return jsonify(
        account_sid,
        api_key,
        api_secret,
        chat_service,
    )

@app.route('/token', methods=['GET'])
def randomToken():
    username = request.values.get("identity")
    return generateToken(username)


@app.route('/token', methods=['POST'])
def createToken(username):
    # Get the request json or form data
    content = request.get_json() or request.form
    # get the identity from the request, or make one up
    identity = content.get('identity', username)
    return generateToken(identity)

@app.route('/token/<identity>', methods=['POST', 'GET'])
def token(identity):
    return generateToken(identity)

def generateToken(identity):

    # Create access token with credentials
    token = AccessToken(account_sid, api_key, api_secret, identity=identity)

    if chat_service:
        chat_grant = ChatGrant(service_sid=chat_service)
        token.add_grant(chat_grant)
    # Return token info as JSON
    return jsonify(identity=identity, token=token.to_jwt().decode('utf-8'))


if __name__ == "__main__":
    app.run(debug=True)
