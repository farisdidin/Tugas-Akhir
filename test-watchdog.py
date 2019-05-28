import sys
import time
import datetime
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from watchdog.events import PatternMatchingEventHandler
from git import Repo

REPO_PATH = "/home/didin/Project/TA/config/tftp"

def create_directory(dirName):
    # try:
    #     os.mkdir(dirName)
    # except:
    #     print("Directory ",dirName, " already exist")
    print("create directory called for "+dirName)

def checkout_commit():
    return commit 

def list_commit(COMMITS_TO_PRINT):
    repo = Repo(REPO_PATH)
    commits = list(repo.iter_commits('master'))[:COMMITS_TO_PRINT]
    for commit in commits:
        print('----')
        print(str(commit.hexsha))
        print("\"{}\" by {} ({}) {}".format(commit.summary,
                                        commit.author.name,
                                        commit.author.email,
                                        commit.tree))
        print(str(commit.authored_datetime))
        print(str("count: {} and size: {}".format(commit.count(),
                                                commit.size)))
        # return list_commit

    

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
            if len(pathSplit) > 1:
                if ".git" not in pathSplit:
                    print(event.event_type)
                    print(event.src_path)
                    print(pathSplit)
                    self.push_repository(repo)
                    print()

    def push_repository(self,repo):
        # try:
        #     dateNow = datetime.datetime.now()
        #     repo.git.add('.')
        #     repo.index.commit(dateNow.strftime("%Y-%m-%d %H-%M-%S"))
        #     origin = repo.remote(name='origin')
        #     origin.push()
        # except:
        #     print("Error Occured")
        # finally:
        #     print("Push completed")

        print("push function are called")

if __name__ == "__main__":
    path = sys.argv if len(sys.argv) > 1 else '.'
    # print (sys.argv[])

    event_handler = EventHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    while True:
        print("\n")
        print("Choose Command :")
        print("1. Create Directory")
        print("2. Checkout ")
        print("3. List Commit")

        command = input()
        if command == "1":
            dirName = input()
            create_directory(dirName)
        elif command =="3":
            number = input("How many commit ? ")
            number = int(number)
            list_commit(number)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
