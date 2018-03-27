# encoding: utf-8
from flask import Flask, request, Response, render_template, jsonify
from twilio.rest import Client
from twilio.jwt.taskrouter.capabilities import WorkerCapabilityToken
from twilio.twiml.voice_response import VoiceResponse, Conference, Enqueue, Dial
from twilio.twiml.messaging_response import Message, MessagingResponse
from twilio.jwt.client import ClientCapabilityToken
import os

app = Flask(__name__, static_folder='app/static')

# Your Account Sid and Auth Token from twilio.com/user/account
account_sid = os.environ.get("TWILIO_ACME_ACCOUNT_SID")
auth_token = os.environ.get("TWILIO_ACME_AUTH_TOKEN")
workspace_sid = os.environ.get("TWILIO_ACME_WORKSPACE_SID") # workspace
workflow_support_sid = os.environ.get("TWILIO_ACME_SUPPORT_WORKFLOW_SID")  # support workflow
workflow_sales_sid = os.environ.get("TWILIO_ACME_SALES_WORKFLOW_SID")  # sales workflow
workflow_billing_sid = os.environ.get("TWILIO_ACME_BILLING_WORKFLOW_SID")  # billing workflow
workflow_mngr_sid = os.environ.get("TWILIO_ACME_MANAGER_WORKFLOW_SID") # manager escalation workfloq
twiml_app = os.environ.get("TWILIO_ACME_TWIML_APP_SID") # Twilio client application SID
caller_id = os.environ.get("TWILIO_ACME_CALLERID") # Contact Center's phone number to be used in outbound communication

client = Client(account_sid, auth_token)

# Create dictionary with activity SIDs
activity = {}
activities = client.taskrouter.workspaces(workspace_sid).activities.list()
for a in activities:
    activity[a.friendly_name] = a.sid

# Private functions

def return_work_space(digits):
    #query user input and assign the correct workflow

    digit_pressed = digits
    if digit_pressed == "1":
        department = "sales"
        work_flow_sid = workflow_sales_sid
        workflowdata = (work_flow_sid, department)  # tuple

        return workflowdata

    if digit_pressed == "2":
        department = "support"
        work_flow_sid = workflow_support_sid
        workflowdata = (work_flow_sid, department) # tuple

        return workflowdata

    if digit_pressed == "3":
        department = "billing"
        work_flow_sid = workflow_billing_sid
        workflowdata = (work_flow_sid, department) # tuple

        return workflowdata


# Main browser entry point - renders index page

@app.route("/", methods=['GET', 'POST'])
def hello_world():
    return render_template('index.html')


# Main IVR entry point - answers phone number's "A Call Comes In" webhook,
# uses <Gather> to select language

@app.route("/incoming_call", methods=['GET', 'POST'])
def incoming_call():
    resp = VoiceResponse()
    with resp.gather(num_digits="1", action="/incoming_call/department", timeout=10) as g:
        g.say("Para Espanol oprime el uno.", language='es')
        g.say("For English, press two.", language='en')
        g.say(u"Pour Francais, pressé trois", language='fr')

    return Response(str(resp), mimetype='text/xml')


# Redirect the user to the correct department for their language choice

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
      'es': ["Para ventas oprime uno", "Para apoyo oprime duo", "Para finanzas oprime tres"],
      'en': ["For sales press one", "For support press two", "For billing press three"],
      'fr': [u"Pour ventes pressé un", u"Pour soutien pressé deux", u"Pour finances pressé tres"]
    }
    with resp.gather(num_digits=digit, action="/enqueue_call?lang="+dept_lang, timeout="10") as g:
        g.say(say_dict.get(dept_lang)[0], language=dept_lang)
        g.say(say_dict.get(dept_lang)[1], language=dept_lang)
        g.say(say_dict.get(dept_lang)[2], language=dept_lang)
    return str(resp)


# Enqueue calls to tasks based on language

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


###################### Agent views ######################

# List of all agents (voice) together with their availability

@app.route("/agent_list", methods=['GET', 'POST'])
def generate_agent_list_view():
    # Create arrays of workers and share that with the template so that workers can be queried on the client side

    # get workers with enabled voice-channel
    voice_workers = client.taskrouter.workspaces(workspace_sid) \
        .workers.list(target_workers_expression="worker.channel.voice.configured_capacity > 0")

    return render_template('agent_list.html', voice_workers=voice_workers)


# Renders individual agent's voice desktop

@app.route("/agents", methods=['GET'])
def generate_view(charset='utf-8'):
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

    # render client/worker tokens to the agent desktop so that they can be queried on the client side
    return render_template('agent_desktop.html', token=client_token.decode("utf-8"),
                           worker_token=worker_token.decode("utf-8"),
                           client_=worker_sid, activity=activity,
                           caller_id=caller_id)


# Renders individual agent's voice desktop without the use of Client.JS

@app.route("/agents/noclient", methods=['GET', 'POST'])
def noClientView():
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
def conference_callback():
    #monitor for when the customer leaves a conference and output something to the console

    if 'StatusCallbackEvent' in request.values and 'CallSid' in request.values:

        cb_event = request.values.get('StatusCallbackEvent')
        conf_moderator = request.values.get('StartConferenceOnEnter')

        if request.values.get("CallSid"):
            call = client.calls(request.values.get("CallSid")).fetch()
            caller = call.from_

            # send a survey message after the call, but make sure to exclude escallations
            if cb_event == "participant-leave" and caller != caller_id:
                if conf_moderator == "true":
                    message = client.messages.create(
                        to=caller,
                        from_=caller_id,
                        body="Thanks for calling OwlCorp, how satisfied were you with your designated agent on a scale of 1 to 10?")
                else:
                    print("Something else happened: " + cb_event)
        return '', 204
    
    return render_template('status.html')

@app.route("/recording_callback", methods=['GET', 'POST'])
def recording_callback():
    if request.values.get('RecordingUrl'):
        print('received recording url: ' + request.values.get('RecordingUrl'))
        return '', 204


@app.route("/callTransfer", methods=['GET', 'POST'])
def transferCall():
    # transfer call
    # put the customer call on hold
    participant = client \
        .conferences(request.values.get('conference')) \
        .participants(request.values.get('participant')) \
        .update(hold=True)

    # create new task for the manager escalation
    # add new attributes on the task for customer from number, customer tasksid, selected_language and conference SID
    
    # todo: manager workflow is set manually for now, scope for making that a variable based on who the worker is selecting to escalate to in the next version   
    task = client.taskrouter.workspaces(workspace_sid).tasks \
        .create(workflow_sid=workflow_mngr_sid, task_channel="voice",
                attributes='{"selected_product":"manager' +
                    '", "selected_language":"' + request.values.get('selected_language') + 
                    '", "conference":"' + request.values.get('conference') +
                    '", "customer":"' + request.values.get('participant') + 
                    '", "customer_taskSid":"' + request.values.get('taskSid') + 
                    '", "from":"' + request.values.get('from') + '"}')

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
    # create TwiML that dials manager to customer conference as a participant

    response = VoiceResponse()
    dial = Dial()
    dial.conference(request.values.get('conference'))
    response.append(dial)

    return Response(str(response), mimetype='text/xml')

if __name__ == "__main__":
    app.run(debug=True)
