'''
    tasker.client
    -------------
    
    A client for interacting with a tasker server.
'''

import tasker

from tasker import server

import argparse

parser = argparse.ArgumentParser(description='Tasker is a tool for keeping track of tasks.')
parser.add_argument('-a', '--add', type=str, required=True, help='add a new task')
parser.add_argument('-p', '--priority', type=str, help='set priority, 1 is highest')
parser.add_argument('-d', '--delete', type=str, help='delete a queued task')
args = parser.parse_args()

if not tasker.SERVER_IS_RUNNING:
    server = server.start()
