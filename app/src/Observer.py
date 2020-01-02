import threading
import sys
import time
import datetime

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from watchdog.events import PatternMatchingEventHandler

from git import Repo, Git

from app.src.ApplicationRepo import ApplicationRepo as ar
from app.Models import Device
from app import db

class ObserverThread(threading.Thread):
    def __init__(self,path,name):
        threading.Thread.__init__(self)
        # self.pause = threading.Event()
        self.repo_path = path
        self.name = name

    def pause_thread(self):
        # self.pause.set()
        self.observer.pause()

    def cont_thread(self):
        # self.pause.clear()
        self.observer.resume()


    def run(self):
        print("thread started")
        # self.path = "./config/tftp"
        self.event_handler = EventHandler(self.name,self.repo_path)
        
        self.observer = PausingObserver()

        self.observer.schedule(self.event_handler, self.repo_path, recursive=True)
        self.observer.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join()

class PausingObserver(Observer):
    def dispatch_events(self, *args, **kwargs):
        if not getattr(self, '_is_paused', False):
            super(PausingObserver, self).dispatch_events(*args, **kwargs)

    def pause(self):
        self._is_paused = True

    def resume(self):
        time.sleep(2)  # allow interim events to be queued
        self.event_queue.queue.clear()
        self._is_paused = False

class EventHandler(PatternMatchingEventHandler):
    def __init__(self,repo_name, repo_path):
        print("shitlyfe")
        print(repo_path)
        print(self)
        to_ignore = '*/'+repo_name
        super(EventHandler, self).__init__(ignore_patterns=["*/.git/*", to_ignore])
        self.repo_name = repo_name
        self.repo_path = repo_path
        self.repository = ar(repo_path,repo_name)
        self.file_cache = {}
    #   super(EventHandler, self).__init__()

    def on_modified(self, event):
        eventType = ["deleted", "modified"]
        global flag_checkout
    
        if event.event_type in eventType:
            seconds = int(time.time())
            key = (seconds, event.src_path)
            if key in self.file_cache:
                return
            self.file_cache[key] = True
            pathSplit = event.src_path.split("/")
            if len(pathSplit) > 4:
                if ".git" not in pathSplit:
                    print(event.event_type)
                    print(event.src_path)
                    print(pathSplit)
                    print(len(pathSplit))
                    print(self.repo_name)
                    if self.repository.check_repo():
                        self.repository.checkout_to_branch()
                        self.repository.push()
                    else:
                        self.repository.create_branch()
                        self.repository.push()
                    
                    record = Device.query.filter_by(device_name=self.repo_name).first()
                    record.device_version = self.repository.get_head()['message']
                    db.session.commit()
                    


                    # self.update_branch()
                    # print("{}-->{}".format(self.repo_name,initialAttributes[self.repo_name]))

                    

        flag_checkout = True

    # def push_repository(self,repo):
    #     try:
    #         dateNow = datetime.datetime.now()
    #         repo.git.add('.')
    #         repo.index.commit(dateNow.strftime("%Y-%m-%d %H-%M-%S"))
    #         # origin = repo.remote(name='origin')
    #         # origin.push()
    #         print(repo)
    #         # print(path)
    #     except Exception as e:
    #         print("Error Occured")
    #         print(e)
    #     finally:
    #         print("Push completed")

    #     print("push function are called")

    
    

    # def create_branch(self):
    #     g = Repo(repos[self.repo_name]['path']).git
    #     num = str(len(initialAttributes[self.repo_name]['branches']))
    #     new_branch = num+'-branch'
    #     initialAttributes[self.repo_name]['branches'].append(new_branch)
    #     g.checkout(b=new_branch)

    

    # def update_branch(self):
    #     x = ApplicationRepo(repos[self.repo_name]['path'], self.repo_name)
    #     initialAttributes[self.repo_name]['branches']=x.get_branches()
    #     initialAttributes[self.repo_name]['hash_branches']=x.get_hash_branches()

