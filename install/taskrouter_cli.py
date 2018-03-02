#!/usr/bin/python
# encoding: utf-8
from twilio.rest import Client
import os
import json
import ntpath
import argparse

account_sid = os.environ.get("TWILIO_ACME_ACCOUNT_SID")
auth_token = os.environ.get("TWILIO_ACME_AUTH_TOKEN")

init_workers = [
    {
        'friendly_name' : 'Francisco',
        'attributes'    : '{"skills":["support","billing","sales"], "languages":["en","es","fr"], "contact_uri":"client:$WORKER_SID$"}',
        'channels'      : ['voice', 'chat']
    },
    {
        'friendly_name' : 'Diego',
        'attributes'    : '{"skills":["support","billing"], "languages":["es","en"], "contact_uri":"client:$WORKER_SID$"}',
        'channels'      : ['voice']
    },
    {
        'friendly_name' : 'Susan',
        'attributes'    : '{"skills":["manager"], "contact_uri":"client:$WORKER_SID$"}',
        'channels'      : ['chat']
    },
    {
        'friendly_name' : 'Giselle',
        'attributes'    : '{"skills":["support", "OOO"], "languages":["en", "fr"], "contact_uri":"client:$WORKER_SID$"}',
        'channels'      : ['voice']
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
        'target_workers'       : 'skills HAS "support"',
    },
    {
        'friendly_name'        : 'Billing',
        'max_reserved_workers' : 10,
        'target_workers'       : 'skills HAS "billing"',
    },
    {
        'friendly_name'        : 'Sales',
        'max_reserved_workers' : 10,
        'target_workers'       : 'skills HAS "sales"',
    },
    {
        'friendly_name'        : 'Off Hours',
        'max_reserved_workers' : 10,
        'target_workers'       : 'skills HAS "OOO"',
    },
    {
        'friendly_name'        : 'Managers',
        'max_reserved_workers' : 10,
        'target_workers'       : 'skills HAS "manager"'
    },
]

# For environment variables output (also see 'env_var' key in init_taskqueues)
ws_env_var = 'TWILIO_ACME_WORKSPACE_SID'

parser = argparse.ArgumentParser(description="Twilio TaskRouter Console Manager")
parser.add_argument("-d", "--delete", help="Delete Workspace and all of its content", dest='action', action='store_const', const='delete')
parser.add_argument("-l", "--list", help="List existing Workspaces", dest='action', action='store_const', const='list')
parser.add_argument("-i", "--init", help="Initialize new Workspace", dest='action', action='store_const', const='init')
parser.add_argument("-e", "--env", help="Also print suggested env setup for Workspace when initializing", dest='env', action='store_const', const=True)
parser.add_argument('--sid', help='Workspace SID', dest='ws_sid')
parser.add_argument('--name', help='Workspace Name', dest='ws_name')
parser.add_argument('--url', help='Event Callback URL', dest='ws_url')


args = parser.parse_args()
if(args.action == None):
    parser.print_help()
    exit

# List
if(args.action == 'list'):
    client = Client(account_sid, auth_token)

    # If no SID was provided, just list all Workspaces
    if(args.ws_sid == None):
        workspaces = client.taskrouter.workspaces.list()

        for workspace in workspaces:
            print(str(workspace.friendly_name), ':', str(workspace.sid))

    # If SID was provided, list details about that one Workspace
    else:
        workspace = client.taskrouter.workspaces(args.ws_sid).fetch()
        print('Workspace ' + str(workspace.friendly_name) + ' : ' + str(workspace.sid))
        
        print('\nWorkers')
        print('  %-10s  %-34s   %-12s   %s' % ('Name', 'SID', 'Languages', 'Skills'))
        workers = client.taskrouter.workspaces(args.ws_sid).workers.list()
        for worker in workers:
            attr = json.loads(worker.attributes)
            skills = ''
            if ('skills' in attr):
                skills = ', '.join(str(skill) for skill in attr['skills'])
            languages = ''
            if ('languages' in attr):
                languages = ', '.join(str(lang) for lang in attr['languages'])
            print('  %-10s  %s   %-12s   %s' % (worker.friendly_name, worker.sid, languages, skills))
            
        print('\nWorker channels')
        print('            ' + ''.join('%-8s' % (task_channel.unique_name,) for task_channel in workspace.task_channels.list()))
        for worker in workers:
            print('  %-10s' % worker.friendly_name) + ''.join('%-8s' % ('x' if worker_channel.available else '',) for worker_channel in worker.worker_channels.list())

        print('\nActivities')
        print('  %-10s  %-34s   %s' % ('Name', 'SID', 'Available'))
        activities = client.taskrouter.workspaces(args.ws_sid).activities.list()
        for activity in activities:
            print('  %-10s  %s   %s' % (activity.friendly_name, activity.sid, activity.available))

        print('\nTaskQueues')
        print('  %-10s  %-34s   %s' % ('Name', 'SID', 'Target Workers'))
        taskqueues = client.taskrouter.workspaces(args.ws_sid).task_queues.list()
        for taskqueue in taskqueues:
            print('  %-10s  %s   %s' % (taskqueue.friendly_name, taskqueue.sid, taskqueue.target_workers))

        print('\nWorkflows')
        print('  %-10s  %-34s' % ('Name', 'SID'))
        workflows = client.taskrouter.workspaces(args.ws_sid).workflows.list()
        for workflow in workflows:
            print('  %-10s  %s' % (workflow.friendly_name, workflow.sid))
            wf_config = json.loads(workflow.configuration)
            print('    %-15s   %s' % ('Filter Name', 'Expression'))
            if 'task_routing' in wf_config and 'filters' in wf_config['task_routing']:
                for filter in wf_config['task_routing']['filters']:
                    print('    %-15s   %s' % (filter['filter_friendly_name'], filter['expression']))

# Delete
if(args.action == 'delete'):
    if(args.ws_sid == None):
        print('Workspace SID must be specified')
        parser.print_help()
        exit
    
    client = Client(account_sid, auth_token)
    workspace = client.taskrouter.workspaces(args.ws_sid).fetch()
    # delete any tasks still pending
    tasks = workspace.tasks.list(assignment_status="pending")
    if tasks:
        print("Pending tasks found - deleting")
        for task in tasks:
            print('  ' + task.sid + ' in ' + task.task_queue_friendly_name)
            task.delete()

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
        
    client = Client(account_sid, auth_token)
    workspace = client.taskrouter.workspaces.create(
        friendly_name=args.ws_name,
        event_callback_url=args.ws_url,
        template='FIFO'
    )
    env = { ws_env_var : workspace.sid }

    wrapup = client.taskrouter.workspaces(workspace.sid).activities \
        .create(friendly_name='WrapUp', available=False)
    print('Default WrapUp : ' + wrapup.sid + ' activity has been created.')

    # Build dictionary of Activity SIDs
    activities = client.taskrouter.workspaces(workspace.sid).activities.list()
    activity_sid = {}
    for activity in activities:
        activity_sid[activity.friendly_name] = activity.sid

    task_channels = workspace.task_channels.list()
    print('Creating workers...')
    for init_worker in init_workers:
        worker = client.taskrouter.workspaces(workspace.sid).workers.create(
            friendly_name=init_worker['friendly_name'], attributes=init_worker['attributes']
        )
        updated_attributes = init_worker['attributes'].replace('$WORKER_SID$', worker.sid)
        worker = worker.update(attributes=updated_attributes)

        # set worker's channels if there are any configured, otherwise leave all on by default
        if 'channels' in init_worker:
            for task_channel in task_channels:
                worker.worker_channels(task_channel.unique_name).update(available=bool(task_channel.unique_name in init_worker['channels']))
        print('  Worker ' + str(worker.friendly_name) + ' : ' + str(worker.sid) + ' has been created.')

    print('Creating TaskQueues...')
    # First delete the default Workflow
    workflows = client.taskrouter.workspaces(workspace.sid).workflows.list()
    for workflow in workflows:
        workflow = client.taskrouter.workspaces(workspace.sid).workflows(workflow.sid).fetch()
        if(workflow.friendly_name == 'Default Fifo Workflow'):
            success = client.taskrouter.workspaces(workspace.sid).workflows(workflow.sid).delete()
            print('  Default Workflow ' + str(workflow.friendly_name) + ' : ' + str(workflow.sid) + ' has been deleted.')
    # Then delete the default TaskQueue
    taskqueues = client.taskrouter.workspaces(workspace.sid).task_queues.list()
    for taskqueue in taskqueues:
        taskqueue = client.taskrouter.workspaces(workspace.sid).task_queues(taskqueue.sid).fetch()
        if(taskqueue.friendly_name == 'Sample Queue'):
            success = client.taskrouter.workspaces(workspace.sid).task_queues(taskqueue.sid).delete()
            print('  Default TaskQueue ' + str(taskqueue.friendly_name) + ' : ' + str(taskqueue.sid) + ' has been deleted.')
    # Now create new TaskQueues
    taskqueue_sid = {}
    for init_tq in init_taskqueues:
        taskqueue = client.taskrouter.workspaces(workspace.sid) \
            .task_queues.create(
                friendly_name=init_tq['friendly_name'],
                reservation_activity_sid=activity_sid['Reserved'],
                assignment_activity_sid=activity_sid['Busy'],
                max_reserved_workers=init_tq['max_reserved_workers'],
                target_workers=init_tq['target_workers'])
        # Build dictionary of TaskQueue SIDs
        taskqueue_sid[init_tq['friendly_name']] = taskqueue.sid
        print('  TaskQueue ' + str(taskqueue.friendly_name) + ' : ' + str(taskqueue.sid) + ' has been created.')

    init_workflows = [
        {
            'friendly_name' : 'Support Workflow',
            'env_var'       : 'TWILIO_ACME_SUPPORT_WORKFLOW_SID',
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
        {
            'friendly_name' : 'Manager Workflow',
            'env_var'       : 'TWILIO_ACME_MANAGER_WORKFLOW_SID',
            'configuration' : {
                'task_routing': {
                    'filters': [
                        {
                            'filter_friendly_name': 'Manager',
                            'expression': 'selected_product == "manager"',
                            'targets': [{'queue': taskqueue_sid['Managers']}]
                        },
                    ],
                }
            }
        },
    ]

    print('Creating Workflows...')
    for init_wf in init_workflows:
        workflow = client.taskrouter.workspaces(workspace.sid).workflows.create(
            friendly_name=init_wf['friendly_name'],
            task_reservation_timeout='120',
            configuration=json.dumps(init_wf['configuration'])
        )
        print('  Workflow ' + str(workflow.friendly_name) + ' : ' + str(workflow.sid) + ' has been created.')
        if(args.env and 'env_var' in init_wf):
            env.update({init_wf['env_var'] : workflow.sid})

    print('Workspace ' + str(args.ws_name) + ' : ' + str(workspace.sid) + ' has been created.')

    if(args.env):
        shell = ntpath.basename(os.environ['SHELL'])
        print('\nEnvironment variables for ' + shell)
        for key, value in env.items():
            if shell=='fish':
                print('set -x ' + key + ' ' + value)
            else:
                print('export ' + key + '=' + value)
