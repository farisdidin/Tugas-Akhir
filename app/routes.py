import collections
import os
import sys
import requests

from flask import jsonify
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin


from app import app
from app.src.ApplicationRepo import ApplicationRepo as ap
from app.src.Observer import ObserverThread as ot

# app.config['SQLALCHEMY_DATABASE_URI']='mysql://didin:Underground23@localhost/tugas_akhir'

repo_details = collections.defaultdict(dict)
path_tftp = "./config/tftp"
path_ftp = "./config/ftp"

for i in os.listdir(path_ftp):
    if os.path.isdir(os.path.join(path_ftp, i)):
        path = os.path.join(path_ftp, i)
        repo_details[i]['path'] = path

for i in os.listdir(path_tftp):
    if os.path.isdir(os.path.join(path_tftp, i)):
        if i not in repo_details:
            path = os.path.join(path_tftp, i)
            repo_details[i]['path'] = path

for i in repo_details:
    thread = ot(repo_details[i]['path'], i)
    repo_details[i]['observer']=thread
    thread.start()

print(repo_details)


@app.route('/login')
def login():
    return render_template('page_login.html')

@app.route('/')
def begin():
    return render_template('dashboard.html')
    # return "API from configuration management"


@app.route('/list_all')
def all_repo():
    repos = []
    for i in repo_details:
        repos.append(i)

    return jsonify(repos)


@app.route('/list/<repo_name>')
def index(repo_name):
    rp = ap(repo_details[repo_name]['path'], repo_name)
    branch = rp.get_branches()
    head_branch = rp.get_hash_branches()
    repo_detail = collections.defaultdict(dict)
    for i in branch:
        repo_detail[i] = head_branch[branch.index(i)]
    return jsonify(repo_detail)


@app.route('/create_repo/<protocol>/<name>')
def create_repo(protocol, name):
    if protocol == 'tftp' or protocol == 'ftp':
        if name not in repo_details:
            path = "./config/"+protocol+"/"+name
            try:
                os.mkdir(path)
                # initiate_file = path+"/intial"
                # f = open(initiate_file,'w+')
                # f.close()
                print("{} {}".format(name, path))
                
                rp = ap(path,name)
                rp.create_gitea_repo()
                rp.pull()
                # rp.push()
                repo_details[name]['path']=path
                thread = ot(path,name)
                thread.start()
                repo_details[name]['observer']=thread
                print(repo_details)
                print("DEBUG")
            except Exception as e:
                print(e)
            finally:
                # print('Repository {} created'.format(name))
                info = 'Repository {} created'.format(name)
                return info
    return "Repository already exist"


@app.route('/checkout/<repo_name>/<commit>')
def checkout(repo_name, commit):
    observer = repo_details[repo_name]['observer']
    observer.pause_thread()
    repository = ap(repo_details[repo_name]['path'],repo_name)
    repository.checkout(commit)
    observer.cont_thread()
    log = repository.get_log()
    return log
        
@app.route('/list_commits/<repo_name>')
def list_commit(repo_name):
    rp = ap(repo_details[repo_name]['path'], repo_name)
    list_of_commits = rp.get_list_commits()
    return jsonify(list_of_commits)

@app.route('/head/<repo_name>')
def current_head(repo_name):
    rp = ap(repo_details[repo_name]['path'], repo_name)
    current_head = rp.get_head()
    if current_head in rp.get_hash_branches():
        index = rp.get_hash_branches().index(current_head)
        info = rp.get_branches()[index]
        print(info)
        print('branch')
    else:
        info = current_head
        print('commit')

    info = 'current head are '+info
    return info