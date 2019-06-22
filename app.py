import sys
import time
import datetime
import os
import collections
import itertools

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from watchdog.events import PatternMatchingEventHandler

import threading

from git import Repo, Git
from flask import Flask,jsonify, request, redirect, render_template, url_for
from flask_script import Manager, Server

flag_checkout = True
observer_global = None

app = Flask(__name__)
REPO_PATH = "/home/didin/Project/TA/config/tftp"

def head_commit(repo_name):
    repo_path = repos[repo_name]['path']
    commit = Repo(repo_path).head.commit
    commit = Repo(repo_path).git.rev_parse(commit,short=7)
    # print(commit)
    return commit

def check_latest_commit():
    repo = Repo(REPO_PATH)
    commits = list(repo.iter_commits('master'))[:1]
    
    head = head_commit(repo_path)
    if head == commits[0]:
        return True
    else:
        return False

class observerThread(threading.Thread):
    def __init__(self,path,name):
        threading.Thread.__init__(self)
        self.pause = threading.Event()
        self.path_observer = path
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
        self.event_handler = EventHandler(self.name)
        
        self.observer = PausingObserver()

        self.observer.schedule(self.event_handler, self.path_observer, recursive=True)
        self.observer.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join()


class ApplicationRepo():
    def __init__(self,repo_path,repo_name):
        self.repo = Repo(repo_path)
        self.repoName = repo_name

    def get_branches(self):
        branch = self.repo.git.branch()
        branch = branch.replace('*','')
        branch = branch.replace(' ','')
        branch_split = branch.split('\n')
        indices = [i for i, s in enumerate(branch_split) if 'HEAD' in s]
        # print(indices)
        if indices:
            del branch_split[indices[0]]
        return branch_split

    def get_hash_branches(self):
        show_ref = self.repo.git.show_ref(hash=7)
        show_ref = show_ref.split('\n')
        return show_ref

    def check_attribute_hash(self):
        global initialAttributes
        current = self.get_hash_branches()
        for i,(a,b) in enumerate(zip(initialAttributes[self.repoName]['hash_branches'],current)):
            if a != b:
                initialAttributes[self.repoName]['hash_branches'][i]=b 




class PausingObserver(Observer):
    def dispatch_events(self, *args, **kwargs):
        if not getattr(self, '_is_paused', False):
            super(PausingObserver, self).dispatch_events(*args, **kwargs)

    def pause(self):
        self._is_paused = True

    def resume(self):
        time.sleep(5)  # allow interim events to be queued
        self.event_queue.queue.clear()
        self._is_paused = False

class EventHandler(PatternMatchingEventHandler):
    def __init__(self,repo_name):
        print("shitlyfe")
        print(self)
        super(EventHandler, self).__init__(ignore_patterns=["*/.git/*", "*/tftp"])
        self.repo_name = repo_name
    #   super(EventHandler, self).__init__()

    def on_any_event(self, event):
        eventType = ["deleted", "modified"]
        global flag_checkout
    
        if event.event_type in eventType:
            pathSplit = event.src_path.split("/")
            if len(pathSplit) > 4:
                if ".git" not in pathSplit:
                    print(event.event_type)
                    print(event.src_path)
                    print(pathSplit)
                    print(len(pathSplit))
                    print(self.repo_name)
                    self.update_branch()
                    if self.check_repo(self.repo_name):
                        self.checkout_to_branch(self.repo_name)
                        repo = Repo(repos[self.repo_name]['path'])
                        self.push_repository(repo)
                    else:
                        self.create_branch()
                        repo = Repo(repos[self.repo_name]['path'])
                        self.push_repository(repo)

                    

        flag_checkout = True

    def push_repository(self,repo):
        try:
            dateNow = datetime.datetime.now()
            repo.git.add('.')
            repo.index.commit(dateNow.strftime("%Y-%m-%d %H-%M-%S"))
            # origin = repo.remote(name='origin')
            # origin.push()
            print(repo)
            # print(path)
        except Exception as e:
            print("Error Occured")
            print(e)
        finally:
            print("Push completed")

        print("push function are called")

    def check_repo(self,repo_name):
        head = head_commit(repo_name)
        if head in initialAttributes[repo_name]['hash_branches']:
            return True
        else:
            return False

    def create_branch(self):
        g = Repo(repos[self.repo_name]['path']).git
        num = str(len(initialAttributes[self.repo_name]['branches']))
        new_branch = num+'branch'
        initialAttributes[self.repo_name]['branches'].append(new_branch)
        g.checkout(b=new_branch)

    def checkout_to_branch(self,repo_name):
        g = Git(repos[self.repo_name]['path'])
        branch_index = initialAttributes[repo_name]['hash_branches'].index(head_commit(repo_name))
        branch = initialAttributes[repo_name]['branches'][branch_index]
        g.checkout(branch)

    def update_branch(self):
        x = ApplicationRepo(repos[self.repo_name]['path'], self.repo_name)
        initialAttributes[self.repo_name]['branches']=x.get_branches()
        initialAttributes[self.repo_name]['hash_branches']=x.get_hash_branches()




@app.route("/")
def hello():
    return "Manajemen Konfigurasi perangkat jaringan"

@app.route("/list_commit/<repo_device>/<COMMITS_TO_PRINT>")
def list_commit(repo_device ,COMMITS_TO_PRINT):
    repo_path = os.path.join(REPO_PATH,repo_device)
    repo = Repo(repo_path)
    COMMITS_TO_PRINT=int(COMMITS_TO_PRINT)
    commits = list(repo.iter_commits('master'))[:COMMITS_TO_PRINT]
    list_of_commit = []
    for commit in commits:
        print('----')
        halo = head_commit(repo_path)
        halo = str(halo)
        commit_str = str(commit.hexsha)
        if commit_str == halo:
            # print("tess")
            # print(str(commit.hexsha)+" <---HEAD")
            short_sha = repo.git.rev_parse(commit.hexsha,short=6)
            print(short_sha)
            # hexha = commit.hexsha+"<--- HEAD"
            hexha = short_sha+"<---- HEAD |||||"
        else:
            # print(str(commit.hexsha))
            short_sha = repo.git.rev_parse(commit.hexsha,short=6)
            print(short_sha)
            hexha = commit.hexsha
            hexha = short_sha

        # print("\"{}\" by {} ({})".format(commit.summary,
        #                                 commit.author.name,
        #                                 commit.author.email
        #                                 ))
        print(str(commit.authored_datetime))
        # print(str("count: {} and size: {}".format(commit.count(),
                                                # commit.size)))
        record = "{} \'{}\' {}".format(hexha,commit.summary, commit.authored_datetime)
        list_of_commit.append(record)
    return jsonify(list_of_commit)

@app.route("/create/<protocol>/<name>")
def create_directory(protocol, name):
    if protocol == 'tftp' or protocol == 'ftp':
        if name not in repos:
            path = "./config/"+protocol+"/"+name
            try:  
                os.mkdir(path)
                Repo.init(path)
                initiate_file = path+"/intial"
                f = open(initiate_file,'w+')
                f.close()
                repo = Repo(path)
                repo.git.add('.')
                repo.index.commit("init")
                if name not in repos:
                    # repos.append(name)
                    repos[name]['path']=path
                    # path_observer = os.path.join(REPO_PATH,name)
                    x = observerThread(path, name)
                    x.start()
                    observer[name]=x
                print(repos)
            except OSError as err:  
                print ("Creation of the directory %s failed" % path)
                error = err
                return error
            else:  
                print ("Successfully created the directory %s " % path)
                return "Successfully created the directory "

    else:
        return "Protocol is not available"



@app.route("/list/<protocol>")
def list_directory(protocol):
    path = "./config/tftp"
    directory = []
    for x in os.listdir(path):
        if x != ".git":
            if os.path.isdir(os.path.join(path,x)):
                directory.append(x)
                print(x)
    return jsonify(directory)

@app.route("/<repo>/checkout/<commit>")
def checkout_commit(repo,commit):
    # global flag_checkout
    # flag_checkout = False
    x = observer[repo]
    x.pause_thread()
    repo_path = repos[repo]['path'] 
    g = Git(repo_path)
    g.checkout(commit)
    x.cont_thread()

    
    return redirect(url_for('list_commit',repo_device=repo ,COMMITS_TO_PRINT=3))

@app.route('/check_current/<repoName>')
def check_current(repoName):
    path = "./config/tftp"
    repo_path = os.path.join(path,repoName)
    x = ApplicationRepo(repo_path,repoName)
    x.check_attribute_hash()

    return 'Checked'

@app.route('/check/<repoName>')
def check(repoName):
    halo = initialAttributes[repoName] 
    print(initialAttributes[repoName])
    return jsonify(halo)

@app.route('/graph/<repoName>')
def graph(repoName):
    path = "./config/tftp"
    repo_path = os.path.join(path,repoName)
    repo = Repo(repo_path)
    graph = repo.git.log(all=True, oneline=True, graph=True)
    return graph

@app.route('/pause/<repo_name>')
def pause(repo_name):
    repoObserver = observer[repo_name]
    repoObserver.pause_thread()
    return repo_name+' is paused'

@app.route('/cont/<repo_name>')
def cont(repo_name):
    repoObserver = observer[repo_name]
    repoObserver.cont_thread()
    return repo_name+' is continued'

if __name__ == '__main__':
    initialAttributes = collections.defaultdict(dict)
    repos = collections.defaultdict(dict)
    observer = collections.defaultdict(dict)
    path_tftp = "./config/tftp"
    path_ftp = "./config/ftp"
    for x in os.listdir(path_tftp):
        if os.path.isdir(os.path.join(path_tftp,x)):
            path_observer = os.path.join(path_tftp,x)
            # repos.append(x)
            repos[x]['path']=os.path.join(path_tftp,x)
            print(x)
            repo_observer = observerThread(path_observer, x)
            repo_observer.start()
            observer[x]=repo_observer

    for x in os.listdir(path_ftp):
        if os.path.isdir(os.path.join(path_ftp,x)):
            if x not in repos:
                path_observer = os.path.join(path_ftp,x)
                # repos.append(x)
                repos[x]['path']=os.path.join(path_ftp,x)
                
                print(x)
                repo_observer = observerThread(path_observer, x)
                repo_observer.start()
                observer[x]=repo_observer

    for a in repos:
        x = ApplicationRepo(repos[a]['path'], a)
        initialAttributes[a]['branches']=x.get_branches()
        initialAttributes[a]['hash_branches']=x.get_hash_branches()
        # print(observer[repos.index(a)])
        print(a)

    
    print("Repos are : ",repos)
    print("Observer are : " ,observer)
    print("Inititial Attribute : ", initialAttributes)
    for a in repos:
        print(a)
    app.run(debug=True, use_reloader=False)
 