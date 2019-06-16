import sys
import time
import datetime
import os

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from watchdog.events import PatternMatchingEventHandler

import threading

from git import Repo, Git
from flask import Flask,jsonify, request, redirect, render_template, url_for

COUNTER = 0

app = Flask(__name__)
REPO_PATH = "/home/didin/Project/TA/config/tftp"

def observer_directory():
    print("thread started")
    path = "./config/tftp"
    event_handler = EventHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

def head_commit():
    commit = Repo(REPO_PATH).head.commit
    # print(commit)
    return commit

class EventHandler(PatternMatchingEventHandler):
    def __init__(self):
        
      super(EventHandler, self).__init__(ignore_patterns=["*/.git/*", "*/tftp"])
    #   super(EventHandler, self).__init__()

    def on_any_event(self, event):
        eventType = ["deleted", "modified"]
        
        # Repo object used to programmatically interact with Git repositories
        repo = Repo(REPO_PATH)
        if event.event_type in eventType:
            pathSplit = event.src_path.split("/")
            if len(pathSplit) > 4:
                if ".git" not in pathSplit:
                    print(event.event_type)
                    print(event.src_path)
                    print(pathSplit)
                    print(len(pathSplit))
                    # path_to_commit = pathSplit[len(pathSplit)-2]+"/"+pathSplit[len(pathSplit)-1]
                    path_to_commit = pathSplit[len(pathSplit)-2]+"/"
                    self.push_repository(repo,path_to_commit)
                    # print(COUNTER)

    def push_repository(self,repo,path):
        try:
            dateNow = datetime.datetime.now()
            repo.git.add('.')
            repo.index.commit(dateNow.strftime("%Y-%m-%d %H-%M-%S"))
            origin = repo.remote(name='origin')
            # origin.push()
            print(repo)
            print(path)
        except Exception as e:
            print("Error Occured")
            print(e)
        finally:
            print("Push completed")

        print("push function are called")

@app.route("/")
def hello():
    return "Manajemen Konfigurasi perangkat jaringan"

@app.route("/list_commit/<COMMITS_TO_PRINT>")
def list_commit(COMMITS_TO_PRINT):
    repo = Repo(REPO_PATH)
    COMMITS_TO_PRINT=int(COMMITS_TO_PRINT)
    commits = list(repo.iter_commits('master'))[:COMMITS_TO_PRINT]
    list_of_commit = []
    for commit in commits:
        print('----')
        halo = head_commit()
        halo = str(halo)
        commit_str = str(commit.hexsha)
        if commit_str == halo:
            print("tess")
            print(str(commit.hexsha)+" <---HEAD")
            hexha = commit.hexsha+"<--- HEAD"
        else:
            print(str(commit.hexsha))
            hexha = commit.hexsha

        # print("\"{}\" by {} ({})".format(commit.summary,
        #                                 commit.author.name,
        #                                 commit.author.email
        #                                 ))
        print(str(commit.authored_datetime))
        # print(str("count: {} and size: {}".format(commit.count(),
                                                # commit.size)))
        record = "{} {} {}".format(hexha,commit.summary, commit.authored_datetime)
        list_of_commit.append(record)
    return jsonify(list_of_commit)

@app.route("/create/<protocol>/<name>")
def create_directory(protocol, name):
    if protocol == 'tftp' or protocol == 'ftp':
        path = "./config/"+protocol+"/"+name
        try:  
            os.mkdir(path)
        except OSError:  
            print ("Creation of the directory %s failed" % path)
            return "Creating directory failed"
        else:  
            print ("Successfully created the directory %s " % path)
            return "Successfully created the directory "

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

@app.route("/checkout/<commit>")
def checkout_commit(commit):
    g = Git(REPO_PATH)
    g.checkout(commit)
    return redirect(url_for('list_commit',COMMITS_TO_PRINT=3))

if __name__ == '__main__':
    x = threading.Thread(target=observer_directory)
    x.start()
    app.run(debug=True)
    # try:
    #     while True:
    #         time.sleep(1)
    # except KeyboardInterrupt:
    #     x.join()