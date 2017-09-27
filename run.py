from flask import Flask, request, Response, render_template
from twilio.rest import Client
from twilio.jwt.taskrouter.capabilities import WorkerCapabilityToken
from twilio.twiml.voice_response import VoiceResponse, Conference, Enqueue, Dial
from twilio.jwt.client import ClientCapabilityToken
import os

app = Flask(__name__,static_folder='app/static')

# Your Account Sid and Auth Token from twilio.com/user/account
account_sid = os.environ.get("TWILIO_ACME_ACCOUNT_SID")
auth_token = os.environ.get("TWILIO_ACME_AUTH_TOKEN")
workspace_sid = os.environ.get("TWILIO_ACME_WORKSPACE_SID")
workflow_sid = os.environ.get("TWILIO_ACME_SUPPORT_WORKFLOW_SID") #support
workflow_sales_sid = os.environ.get("TWILIO_ACME_SALES_WORKFLOW_SID") #sales
workflow_billing_sid = os.environ.get("TWILIO_ACME_BILLING_WORKFLOW_SID") #billing
workflow_OOO_sid = os.environ.get("TWILIO_ACME_OOO_SID")

twiml_app = os.environ.get("TWILIO_ACME_TWIML_APP_SID")
caller_id = os.environ.get("TWILIO_ACME_CALLERID")

client = Client(account_sid, auth_token)
#private functions

def return_work_space(digits):

    digit_pressed = digits
    if digit_pressed == "1":
        department = "sales"
        work_flow_sid = workflow_sales_sid
        workflowdata = (work_flow_sid, department) #tuple

        return workflowdata

    if digit_pressed == "2":
        department = "support"
        work_flow_sid = workflow_sid
        workflowdata = (work_flow_sid, department)

        return workflowdata

    if digit_pressed == "3":
        department = "billing"
        work_flow_sid = workflow_billing_sid
        workflowdata = (work_flow_sid, department)

        return workflowdata

#Render index

@app.route("/", methods=['GET', 'POST'])
def hello_world():
    return render_template('index.html')

#Default route for support line voice request url

@app.route("/incoming_call", methods=['GET', 'POST'])
def incoming_call():

    resp = VoiceResponse()
    with resp.gather(num_digits="1", action="/incoming_call/department", timeout=10) as g:
        g.say("Para Espanol oprime el uno.", language='es')
        g.say("For English, press two.", language='en')
        g.say("Pour Francais, pressé un", language='fr')

    return Response(str(resp), mimetype='text/xml')

##################################################################

@app.route("/incoming_call/department", methods=['POST', 'GET'])
def choose_dept():
    resp = VoiceResponse()

    if 'Digits' in request.values:
        # Get which digit the caller chose
        choice = request.values['Digits']
        if choice == "1":
            resp.redirect("/dept/es")
            return str(resp)

        if choice == "2":
            resp.redirect("/dept/en")
            return str(resp)

        if choice == "3":
            resp.redirect("/dept/fr")
            return str(resp)

#Select department

@app.route("/dept/es", methods=["GET","POST"])
def es_dept():
    resp = VoiceResponse()
    with resp.gather(num_digits="1", action="/enqueue_call_es", timeout="10") as g:
        g.say("Para sales oprime uno", language='es')
        g.say("Para support oprime duo", language='es')
        g.say("para billing oprime tres", language='es')
    return str(resp)

@app.route("/dept/en", methods=["GET","POST"])
def en_dept():
    resp = VoiceResponse()
    with resp.gather(num_digits="1", action="/enqueue_call_en", timeout="10") as g:
        g.say("For Sales press one", language='en')
        g.say("For Support press two", language='en')
        g.say("For Billing press three", language='en')
    return str(resp)

@app.route("/dept/fr", methods=["GET","POST"])
def fr_dept():
    resp = VoiceResponse()

    with resp.gather(num_digits="1", action="/enqueue_call_fr", timeout="10") as g:
        g.say("Pour sales pressé un", language='fr')
        g.say("Pour support pressé deux", language='fr')
        g.say("Pour billing pressé tres", language='fr')
    return str(resp)

#Enqueue calls to tasks based on language

@app.route("/enqueue_call_es", methods=["GET","POST"])
def enqueue_call_es():
    if 'Digits' in request.values:
        digit_pressed = request.values['Digits']
        workflow_d = return_work_space(digit_pressed)
        resp = VoiceResponse()

        with resp.enqueue(None, workflow_Sid=workflow_d[0]) as e:
            e.task('{"selected_language" : "es", "selected_product" : "' + workflow_d[1] + '"}')
        return Response(str(resp), mimetype='text/xml')
    else:
        resp = VoiceResponse()
        resp.say("no digits detected")
    return Response(str(resp), mimetype='text/xml')

@app.route("/enqueue_call_en", methods=["GET","POST"])
def enqueue_call_en():

    if 'Digits' in request.values:
        digit_pressed = request.values['Digits']
        workflow_d = return_work_space(digit_pressed)
        resp = VoiceResponse()

        with resp.enqueue(None, workflow_Sid=workflow_d[0]) as e:
            e.task('{"selected_language" : "en", "selected_product" : "' + workflow_d[1] + '"}')
        return Response(str(resp), mimetype='text/xml')
    else:
        resp = VoiceResponse()
        resp.say("no digits detected")
    return Response(str(resp), mimetype='text/xml')

@app.route("/enqueue_call_fr", methods=["GET","POST"])
def enqueue_call_fr():

    if 'Digits' in request.values:
        digit_pressed = request.values['Digits']
        workflow_d = return_work_space(digit_pressed)
        resp = VoiceResponse()

        with resp.enqueue(None, workflow_Sid=workflow_d[0]) as e:
            e.task('{"selected_language" : "fr", "selected_product" : "' + workflow_d[1] + '"}')
        return Response(str(resp), mimetype='text/xml')
    else:
        resp = VoiceResponse()
        resp.say("no digits detected")
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
    workers = client.taskrouter.workspaces(workspace_sid).workers.list()
    worker_list = []

    for worker in workers:
        worker_list.append(worker.sid)
        worker_list.append(worker.friendly_name)

    return render_template('agent_list.html', workers= worker_list)


@app.route("/agents", methods=['GET'])
def generate_view(charset='utf-8'):

    worker_sid = request.args.get('WorkerSid') #TaskRouter Worker Token
    worker_capability = WorkerCapabilityToken(
        account_sid = account_sid,
        auth_token = auth_token,
        workspace_sid = workspace_sid,
        worker_sid = worker_sid
    ) #generate worker capability token

    worker_capability.allow_update_activities()
    worker_capability.allow_update_reservations()
    worker_token = worker_capability.to_jwt(ttl=28800)

    capability = ClientCapabilityToken(account_sid, auth_token) #agent Twilio Client capability token
    capability.allow_client_outgoing(twiml_app)
    capability.allow_client_incoming(worker_sid)

    client_token = capability.to_jwt()


    return render_template('client.html', token=client_token.decode("utf-8"), worker_token=worker_token.decode("utf-8"), client_name=worker_sid)

#Callbacks

@app.route("/conference_callback", methods=['GET', 'POST'])
def handle_callback():

 #   if 'StatusCallbackEvent' in  request.values:
 #
 #      cb_event = request.values.get('StatusCallbackEvent')
 #      conf_mod = request.values.get('StartConferenceOnEnter')
 #      reservation_sid  = request.values.get('ReservationSid')
 #      task_sid = request.values.get('TaskSid')
 #      print(cb_event)
 #
 #      if cb_event == "participant-leave":
 #          if conf_mod == "true":
 #              print("customer has left the conference!")   #customer has left so update the worker status to wrap up and update the agent call to completed
 #
 #              reservation = client.taskrouter.workspaces(workspace_sid) \
 ##                 .tasks(task_sid).reservations(reservation_sid).fetch()
 #             worker_sid = reservation.worker_sid
 #
 #              worker = client.taskrouter.workspaces(workspace_sid) \
 #                  .workers(worker_sid).update(activity_sid="WA1734410947caec098f53ed4f29e35732")
 #
 #              from_number = request.args.get('from')


 #          return render_template('status.html', from_number=from_number)
    return render_template('status.html')

@app.route("/callTransfer", methods=['GET', 'POST'])
def transferCall():
    #blind transfer put the call on hold

    participant = client \
        .conferences(request.values.get('conference')) \
        .participants(request.values.get('participant')) \
        .update(hold=True)


    task = client.taskrouter.workspaces(workspace_sid).tasks \
        .create(workflow_sid="WW4af8717df650b33eaaf1b9e5f52d8014", attributes='{"selected_product":"manager", "conference":"' + request.values.get('conference') + '", "customer":"' + request.values.get("customer") + '", "customer_taskSid":"' + request.values.get('taskSid') +'"}')

    print(task.attributes)

    return render_template('status.html')

@app.route("/callmute", methods=['GET', 'POST'])
def unmuteCall():
    #put the call on hold

    participant = client \
        .conferences(request.values.get('conference')) \
        .participants(request.values.get('participant')) \
        .update(hold=request.values.get('muted'))



    return render_template('status.html')


@app.route("/transferTwiml", methods=['GET', 'POST'])
def transferToManager():

    response = VoiceResponse()
    dial = Dial()
    dial.conference(request.values.get('conference'))
    response.append(dial)
    print(response)
    return Response(str(response), mimetype='text/xml')

if __name__ == "__main__":
    app.run(debug=True)