import collections
import os
import shutil
import sys
import requests
import socket

from flask import jsonify, request, Response, redirect, url_for, render_template, flash 
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
# from flask_sqlalchemy import SQLAlchemy
# from flask_admin import Admin


from app import app
from app import db
from app import var

from app.src.ApplicationRepo import ApplicationRepo as ap
from app.src.Observer import ObserverThread as ot
from app.src.Repository import Repository as local_repo

# Thread receiver
from app.src.ObserverReceive import ObserverThread as receiver
from app import var

from app.Models import Device, User

repo_details = collections.defaultdict(dict)

OBSERVER = collections.defaultdict(dict)

devices = Device.query.order_by(Device.device_name).all()
for device in devices:
    thread = ot(device.device_repo_path,device.device_name)
    
    # Thread receiver
    path_thread_2 = os.path.join(var.PATH_RECEIVE, device.device_name)
    thread2 = receiver(path_thread_2,device.device_name)
    thread2.start()
    
    OBSERVER[device.device_name]['observer']=thread
    thread.start()

path_repo = var.PATH
# for i in os.listdir(path_repo):
#     if os.path.isdir(os.path.join(path_repo, i)):
#         path = os.path.join(path_repo, i)
#         repo_details[i]['path'] = path


# for i in repo_details:
#     thread = ot(repo_details[i]['path'], i)
#     repo_details[i]['observer']=thread
#     thread.start()

print(OBSERVER)
print(repo_details)


@app.route('/v2/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        
        if not user or not check_password_hash(user.password, password): 
            flash('Please check your login details and try again.')
            return redirect(url_for('login'))

        login_user(user)
        return redirect(url_for('create'))

@app.route('/v2/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user:
            flash('Username already exist')
            return redirect(url_for('register'))
        
        new_user = User(username=username, password=generate_password_hash(password, method='sha256'))
        db.session.add(new_user)
        db.session.commit()

    return redirect(url_for('login'))

@app.route('/v2/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/list/<repo_name>')
def index(repo_name):
    rp = ap(repo_details[repo_name]['path'], repo_name)
    branch = rp.get_branches()
    head_branch = rp.get_hash_branches()
    repo_detail = collections.defaultdict(dict)
    for i in branch:
        repo_detail[i] = head_branch[branch.index(i)]
    return jsonify(repo_detail)

@app.route('/create/<name>')
def create_repo(name):
    response =  collections.defaultdict(dict)
    if name not in repo_details:
        path = path_repo+"/"+name
        
        # path = "./config/"+protocol+"/"+name
        try:
            os.mkdir(path)
            # initiate_file = path+"/intial"
            # f = open(initiate_file,'w+')
            # f.close()
            print("{} {}".format(name, path))
            
            rp = ap(path,name)
            # rp.create_gitea_repo()
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
            response['result']= info
            return jsonify(response)
    response['result']= "Repository already exist" 
    return jsonify(response)

@app.route('/remove/<repo>')
def remove(repo):
    response =  collections.defaultdict(dict)
    if repo in repo_details:
        path = repo_details[repo]['path']
        shutil.rmtree(path)
        del repo_details[repo] 
        response["result"] = "repository "+repo+" is successfully removed" 
        print(response)
    
    return jsonify(response)


@app.route('/checkout/<repo_name>/<commit>')
def checkout_commit(repo_name, commit):
    observer = repo_details[repo_name]['observer']
    observer.pause_thread()
    repository = ap(repo_details[repo_name]['path'],repo_name)
    repository.checkout(commit)
    observer.cont_thread()
    # log = repository.get_log()
    commit = repository.get_list_commits()
    return jsonify(commit)
        
@app.route('/list_commits/<repo_name>')
def list_commit(repo_name):
    record = Device.query.filter_by(device_name=repo_name).first()
    rp = ap(record.device_repo_path, repo_name)
    list_of_commits = rp.get_list_commits()
    return jsonify(list_of_commits)

@app.route('/head/<repo_name>')
def current_head(repo_name):
    response =  collections.defaultdict(dict)
    record = Device.query.filter_by(device_name=repo_name).first()
    rp = ap(record.device_repo_path, repo_name)
    current_head = rp.get_head()['commit']
    hash_head = current_head
    if current_head in rp.get_hash_branches():
        index = rp.get_hash_branches().index(current_head)
        info = rp.get_branches()[index]
        print(info)
        print('branch')
    else:
        info = current_head
        print('commit')

    # info =hash_head+" "+info
    response["branch"] = info
    response["hash"] = hash_head
     
    return jsonify(response)
    # return hash_head


@app.route('/directory/<repo_name>')
def directory(repo_name):
    response =  collections.defaultdict(dict)
    path1 = os.path.join(path_repo,repo_name)
    # path2 = os.path.join(path_tftp,repo_name)
    if os.path.exists(path1):
        response['result'] = True
    # elif os.path.exists(path2):
    #     response['result'] = True
    else:
        response['result'] = False

    return jsonify(response)


@app.route('/v2')
def home():
    return redirect(url_for('create'))

@app.route('/v2/home', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        name = request.form.get('name')
        address = request.form.get('address')
        try:
            device = Device(device_name=name, device_ip=address, device_repo_path='', device_version='')
            db.session.add(device)
            db.session.commit()
            repo = local_repo(name)
            path,version = repo.create()
            device_record = Device.query.filter_by(device_name=name).first()
            device_record.device_repo_path = path 
            device_record.device_version = version 
            db.session.commit()
            OBSERVER[name]['observer'] = ot( device_record.device_repo_path, device_record.device_name)
            OBSERVER[name]['observer'].start()
            repo_receiver = receiver(os.path.join(var.PATH_RECEIVE,name),name)
            repo_receiver.start() 
        except Exception as e:
            # print("Unexpected error:", sys.exc_info()[0])
            print("menampilkan"+ str(e))
            
        print(name)
        return redirect(url_for('create'))

    if request.method == 'GET':
        devices = Device.query.order_by(Device.device_name).all()
        for device in devices:
            print("name : "+device.device_name)
            print("address : "+device.device_ip)
        hostname = socket.gethostname()    
        IPAddr = socket.gethostbyname(hostname)
        return render_template('dashboard.html', devices=devices, Address=IPAddr)

@app.route('/v2/<repo>/branch/<branchname>')
@login_required
def repo(repo, branchname):
    device_record = Device.query.filter_by(device_name=repo).first()
    path = device_record.device_repo_path
    rp = ap(path, repo)
    files = local_repo(repo).get_files()
    list_of_commits,branches,head = rp.get_list_commits()
    hostname = socket.gethostname()    
    IPAddr = socket.gethostbyname(hostname) 
    return render_template('repo.html', commits=list_of_commits[branchname], reponame=repo, branches=branches, branch=branchname, Address=IPAddr, files=files, head=head)

@app.route('/v2/show/<repo>/<filename>')
@login_required
def show(repo, filename):
    device_record = Device.query.filter_by(device_name=repo).first()
    path = device_record.device_repo_path
    file_path = os.path.join(path,filename)
    with open(file_path,"r") as f:
        content = f.read()

    return Response(content, mimetype='text/plain')

@app.route('/v2/checkout/<repo>/<branch>/<commit>')
@login_required
def checkout(repo,branch, commit):
    observer = OBSERVER[repo]['observer']
    observer.pause_thread()
    device_record = Device.query.filter_by(device_name=repo).first()
    path = device_record.device_repo_path
    repository = ap(path,repo)
    repository.checkout(commit)
    observer.cont_thread()
    # log = repository.get_log()
    commit = repository.get_list_commits()
    return redirect(url_for('repo', repo=repo, branchname=branch))

@app.route('/v2/delete/<repo>')
@login_required
def delete(repo):
    device_record = Device.query.filter_by(device_name=repo).first()
    path = device_record.device_repo_path
    repoapp = ap(path,repo)
    repoapp.remove_gitea_repo()
    db.session.delete(device_record)
    db.session.commit()
    # shutil.rmtree(path)
    # shutil.rmtree()
    repos = local_repo(repo)
    repos.remove()
    print(path)
    return redirect(url_for('create'))


    
    

