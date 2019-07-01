import collections
import os
import sys
from flask import jsonify

from app import app
from app.src.ApplicationRepo import ApplicationRepo as ap
from app.src.Observer import ObserverThread as ot 


repo_path = collections.defaultdict(dict)
path_tftp = "./config/tftp"
path_ftp = "./config/ftp"

for i in os.listdir(path_ftp):
    if os.path.isdir(os.path.join(path_ftp,i)):
        path = os.path.join(path_ftp,i)
        repo_path[i]=path

for i in os.listdir(path_tftp):
    if os.path.isdir(os.path.join(path_tftp,i)):
        if i not in repo_path:
            path = os.path.join(path_tftp,i)
            repo_path[i]=path

for i in repo_path:
	thread = ot(repo_path[i],i)
	thread.start()

@app.route('/')
def begin():
    return "API from configuration management"

@app.route('/list_all')
def all_repo():
	repo = []
	for i in repo_path:
		repo.append(i)

	return jsonify(repo)

@app.route('/list/<repo_name>')
def index(repo_name):
    rp = ap(repo_path[repo_name],repo_name)
    branch = rp.get_branches()
    head_branch = rp.get_hash_branches()
    repo_detail = collections.defaultdict(dict)
    for i in branch:
        repo_detail[i]=head_branch[branch.index(i)]
    return jsonify(repo_detail)


