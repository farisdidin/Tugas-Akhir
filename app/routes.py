import collections
import os
import sys
from flask import jsonify

from app import app
from app.src.ApplicationRepo import ApplicationRepo as ap
from app.src.Observer import ObserverThread as ot


repo = collections.defaultdict(dict)
path_tftp = "./config/tftp"
path_ftp = "./config/ftp"

for i in os.listdir(path_ftp):
    if os.path.isdir(os.path.join(path_ftp, i)):
        path = os.path.join(path_ftp, i)
        repo[i]['path'] = path

for i in os.listdir(path_tftp):
    if os.path.isdir(os.path.join(path_tftp, i)):
        if i not in repo:
            path = os.path.join(path_tftp, i)
            repo[i]['path'] = path

for i in repo:
    thread = ot(repo[i]['path'], i)
    repo[i]['observer']=thread
    thread.start()

print(repo)

@app.route('/')
def begin():

    return "API from configuration management"


@app.route('/list_all')
def all_repo():
    repos = []
    for i in repo:
        repos.append(i)

    return jsonify(repos)


@app.route('/list/<repo_name>')
def index(repo_name):
    rp = ap(repo[repo_name]['path'], repo_name)
    branch = rp.get_branches()
    head_branch = rp.get_hash_branches()
    repo_detail = collections.defaultdict(dict)
    for i in branch:
        repo_detail[i] = head_branch[branch.index(i)]
        return jsonify(repo_detail)


@app.route('/create_repo/<protocol>/<name>')
def create_repo(protocol, name):
    if protocol == 'tftp' or protocol == 'ftp':
        if name not in repo:
            path = "./config/"+protocol+"/"+name
            # try:
            os.mkdir(path)
            initiate_file = path+"/intial"
            f = open(initiate_file,'w+')
            f.close()
            print("{} {}".format(name, path))
            
            rp = ap(path,name)
            rp.push()
            thread = ot(path,name)
            thread.start()
            print("DEBUG")
            # except Exception as e:
                # print(e)
            # finally:
                # print('Repository {} created'.format(name))
    return "Repository created"
        
@app.route('/pause/<repo_name>')
def pause(repo_name):
    observer = repo[repo_name]['observer']
    observer.pause_thread()
    return "paused"

@app.route('/cont/<repo_name>')
def cont(repo_name):
    observer = repo[repo_name]['observer']
    observer.cont_thread()
    return "continued"