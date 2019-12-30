import os
from app import var
from app.src.ApplicationRepo import ApplicationRepo as ar 

class Repository():
    def __init__(self, repo_name):
        self.path = var.PATH
        self.name = repo_name
        
    
    def create(self):
        path_create = self.path+'/'+self.name
        os.mkdir(path_create)
        repo = ar(path_create,self.name)
        repo.create_gitea_repo()
        repo.pull()
        version = repo.get_head()['message']
        return path_create, version