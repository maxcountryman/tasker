'''
    tasker.server
    -------------
    
    This is the server logic for the task manager program.
'''

import os
import sys
import time
import threading
import itertools
import subprocess
import shlex

from heapq import heappush, heappop

INVALID = 0
SECONDS = 60.0
WAITFOR = 30.0


class TaskServer(threading.Thread):
    
    def __init__(self):
        threading.Thread.__init__(self)
        self.pq = []    # priority queue
        self.tasks = {} # queued tasks
        self.counter = itertools.count(1)
        self.daemon = True
        self.start()
    
    def _notify(self, title, task):
        '''This internal method is a multi-platform notifier for tasks. It 
        will attempt to detect your operating system and thereby use the 
        appropriate notify module.
        
        If none is found either one will have to be installed or the program 
        will not yet have a way of notifying on the specified platform in 
        which case the program will exit.
        
        :param:title: The title of the event
        :param:task: The task itself, i.e. a string representing the task
        '''
        
        platform = os.uname()[0]
        
        if platform == 'Darwin':
            cmds = 'growlnotify -m ' + '"' + task + '"' + ' ' + '"' + title + '"'
            args = shlex.split(cmds)
            subprocess.Popen(args)
        elif platform == 'Linux':
            # Alex, use whatever nofity module is good :D
            pass
        else:
            print 'Your platform is currently not supported'
            sys.exit()
    
    def _get_top_priority(self):
        '''This internal method determins the top priority in the list of 
        tasks. Once a task is popped from the list it is subsequently deleted 
        from the task queuing dictionary, `task`. It then returns the time 
        within which to complete the task and the task itself.
        '''
        
        priority, count, _time, task = heappop(self.pq)
        del self.tasks[task]
        if count is not INVALID: # hasn't been deleted
            return (_time, task)
    
    def _monitor(self, wait=WAITFOR):
        '''This internal method checks for queued tasks once every n number 
        of seconds, as specified by `wait`. 
        
        Default is 30 seconds.
        '''
        
        while True:
            time.sleep(wait) # check once per `wait` seconds
            while self.tasks:
                _time, task = self._get_top_priority()
                self._notify('New Task', task)
                time.sleep(_time * SECONDS) # wait for the duration of the task
                self._notify('Times up!', 'The time has expired for the current task')
    
    def add_task(self, task, _time, priority=0, count=None):
        '''Adds a task, `task` to the priority queue. Each task is associated 
        with an alloted amount of time, `_time`. Time is specified in minutes. 
        A priority, `priority` may be specified. 
        
        1 indicates the highest priority. Tasks of the same priority are 
        filtered and prioritized by their position in the priority queue, 
        ensured by `count`.
        '''
        
        if count is None:
            count = next(self.counter)
        entry = [priority, count, _time, task]
        self.tasks[task] = entry
        heappush(self.pq, entry)
    
    def delete_task(self, task):
        '''Sets a task's, `task`, count to `INVALID` thus preventing it from 
        being executed later on, i.e. deletes it.
        '''
        
        task = self.tasks.get(task)
        if not task:
            return
        task[1] = INVALID
    
    def reprioritize(self, priority, task):
        '''Re-adds a task to the `cls.tasks` dictionary, alterting the 
        priority while maintaining its position.
        
        The original task's count is set to `INVALID` thus preventing it from 
        being executed later on, i.e. deletes it.
        '''
        
        entry = self.tasks[task]
        self.add_task(priority, task, entry[2], entry[1])
        entry[1] = INVALID
    
    def run(self):
        self._monitor()

