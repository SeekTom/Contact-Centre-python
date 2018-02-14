#!/usr/bin/python
# encoding: utf-8
from twilio.rest import Client
import os
import json
import argparse

account_sid = os.environ.get("TWILIO_ACME_ACCOUNT_SID")
auth_token = os.environ.get("TWILIO_ACME_AUTH_TOKEN")

init_workers = [
    {
        'friendly_name' : 'Francisco',
        'attributes'    : '{"skills":["support","billing","sales","chat"], "languages":["en","es","fr"], "contact_uri":"client:$WORKER_SID$"}'
    },
    {
        'friendly_name' : 'Diego',
        'attributes'    : '{"skills":["support","billing"], "languages":["es","en"], "contact_uri":"client:$WORKER_SID$"}'
    },
    {
        'friendly_name' : 'Susan',
        'attributes'    : '{"skills":["manager"], "contact_uri":"client:$WORKER_SID$"}'
    },
    {
        'friendly_name' : 'Giselle',
        'attributes'    : '{"skills":["support", "OOO"], "languages":["en", "fr"], "contact_uri":"client:$WORKER_SID$"}'
    },
    {
        'friendly_name' : 'Manny',
        'attributes'    : '{"skills":["manager"], "contact_uri":"client:$WORKER_SID$"}'
    },
]

init_taskqueues = [
    {
        'friendly_name'        : 'Support',
        'max_reserved_workers' : 10,
        'target_workers'       : 'skills HAS "support"'
    },
    {
        'friendly_name'        : 'Billing',
        'max_reserved_workers' : 10,
        'target_workers'       : 'skills HAS "billing"'
    },
    {
        'friendly_name'        : 'Sales',
        'max_reserved_workers' : 10,
        'target_workers'       : 'skills HAS "sales"'
    },
    {
        'friendly_name'        : 'Off Hours',
        'max_reserved_workers' : 10,
        'target_workers'       : 'skills HAS "OOO"'
    },
    {
        'friendly_name'        : 'Managers',
        'max_reserved_workers' : 10,
        'target_workers'       : 'skills HAS "manager"'
    },
]

client = Client(account_sid, auth_token)

parser = argparse.ArgumentParser(description="Twilio TaskRouter Console Manager")
parser.add_argument("-d", "--delete", help="Delete Workspace and all of its content", dest='action', action='store_const', const='delete')
parser.add_argument("-l", "--list", help="List existing Workspaces", dest='action', action='store_const', const='list')
parser.add_argument("-i", "--init", help="Initialize new Workspace", dest='action', action='store_const', const='init')
parser.add_argument('--sid', help='Workspace SID', dest='ws_sid')
parser.add_argument('--name', help='Workspace Name', dest='ws_name')
parser.add_argument('--url', help='Event Callback URL', dest='ws_url')

args = parser.parse_args()
#print(args)
if(args.action == None):
    parser.print_help()
    exit


# List
if(args.action == 'list'):
    client = Client(account_sid, auth_token)
    workspaces = client.taskrouter.workspaces.list()

    for workspace in workspaces:
        print str(workspace.friendly_name), ':', str(workspace.sid)


# Delete
if(args.action == 'delete'):
    if(args.ws_sid == None):
        print('Workspace SID must be specified')
        parser.print_help()
        exit
    
    client = Client(account_sid, auth_token)
    workspace = client.taskrouter.workspaces(args.ws_sid).fetch()

    success = client.taskrouter.workspaces(args.ws_sid).delete()
    if(success):
        print('Workspace ' + str(workspace.friendly_name) + ' : ' + str(workspace.sid) + ' has been deleted.')
    else:
        print('Deleting workspace ' + str(workspace.friendly_name) + ' : ' + str(workspace.sid) + ' has failed.')


# Init
if(args.action == 'init'):
    if(args.ws_name == None):
        print('Workspace Name must be specified')
        parser.print_help()
        exit
        
    workspace = client.taskrouter.workspaces.create(
        friendly_name=args.ws_name,
        event_callback_url=args.ws_url,
        template='FIFO'
    )

    wrapup = client.taskrouter.workspaces(workspace.sid).activities \
        .create(friendly_name='WrapUp', available='false')
    print('Default WrapUp : ' + wrapup.sid + ' activity has been created.')

    # build dictionary of Activity SIDs
    activities = client.taskrouter.workspaces(workspace.sid).activities.list()
    activity_sid = {}
    for activity in activities:
        activity_sid[activity.friendly_name] = activity.sid

    print('Creating workers...')
    for init_worker in init_workers:
        worker = client.taskrouter.workspaces(workspace.sid).workers.create(
            friendly_name=init_worker['friendly_name'], attributes=init_worker['attributes']
        )
        updated_attributes = init_worker['attributes'].replace('$WORKER_SID$', worker.sid)
        worker = worker.update(attributes=updated_attributes)
        print('  Worker ' + str(worker.friendly_name) + ' : ' + str(worker.sid) + ' has been created.')

    print('Creating TaskQueues...')
    # First delete the default workflow
    workflows = client.taskrouter.workspaces(workspace.sid).workflows.list()
    for workflow in workflows:
        workflow = client.taskrouter.workspaces(workspace.sid).workflows(workflow.sid).fetch()
        if(workflow.friendly_name == 'Default Fifo Workflow'):
            success = client.taskrouter.workspaces(workspace.sid).workflows(workflow.sid).delete()
            print('  Default Workflow ' + str(workflow.friendly_name) + ' : ' + str(workflow.sid) + ' has been deleted.')
    # Then delete the default taskqueue
    taskqueues = client.taskrouter.workspaces(workspace.sid).task_queues.list()
    for taskqueue in taskqueues:
        taskqueue = client.taskrouter.workspaces(workspace.sid).task_queues(taskqueue.sid).fetch()
        if(taskqueue.friendly_name == 'Sample Queue'):
            success = client.taskrouter.workspaces(workspace.sid).task_queues(taskqueue.sid).delete()
            print('  Default TaskQueue ' + str(taskqueue.friendly_name) + ' : ' + str(taskqueue.sid) + ' has been deleted.')
    # Now create the new ones
    taskqueue_sid = {}
    for init_tq in init_taskqueues:
        taskqueue = client.taskrouter.workspaces(workspace.sid) \
            .task_queues.create(
                friendly_name=init_tq['friendly_name'],
                reservation_activity_sid=activity_sid['Reserved'],
                assignment_activity_sid=activity_sid['Busy'],
                max_reserved_workers=init_tq['max_reserved_workers'],
                target_workers=init_tq['target_workers'])
        taskqueue_sid[init_tq['friendly_name']] = taskqueue.sid
        print('  TaskQueue ' + str(taskqueue.friendly_name) + ' : ' + str(taskqueue.sid) + ' has been created.')

    init_workflows = [
        {
            'friendly_name' : 'Support Workflow',
            'configuration' : {
                'task_routing': {
                    'filters': [
                        {
                            'filter_friendly_name': 'Support',
                            'expression': 'selected_product == "support"',
                            'targets': [{'queue': taskqueue_sid['Support'],
                                         'expression': 'task.selected_language IN worker.languages'}]
                        },
                    ],
                    'default_filter': {
                        'queue': taskqueue_sid['Support']
                    }
                }
            }
        },
    ]

    print('Creating Workflows...')
    # Now create the new ones
    for init_wf in init_workflows:
        workflow = client.taskrouter.workspaces(workspace.sid).workflows.create(
            friendly_name=init_wf['friendly_name'],
            task_reservation_timeout='120',
            configuration=json.dumps(init_wf['configuration'])
        )
        print('  Workflow ' + str(workflow.friendly_name) + ' : ' + str(workflow.sid) + ' has been created.')


    print('Workspace ' + str(args.ws_name) + ' : ' + str(workspace.sid) + ' has been created.')