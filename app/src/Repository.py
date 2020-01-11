import shutil
import os
from app import var
from app.src.ApplicationRepo import ApplicationRepo as ar 

class Repository():
    def __init__(self, repo_name):
        self.path = var.PATH
        self.path_receiver = var.PATH_RECEIVE
        self.name = repo_name
        self.path_create = self.path+'/'+self.name
        self.path_create2 = self.path_receiver+'/'+self.name
        
    
    def create(self):
        os.mkdir(self.path_create)
        os.mkdir(self.path_create2)
        repo = ar(self.path_create,self.name)
        repo.create_gitea_repo()
        repo.pull()
        version = repo.get_head()['message']
        return self.path_create, version

    def get_files(self):
        files = os.listdir(self.path_create)
        result = []
        for f in files:
            if not f.startswith('.'):
                result.append(f)
        return result
    
    def remove(self):
        # remove_path = self.path_create
        shutil.rmtree(self.path_create)
        shutil.rmtree(self.path_create2)
        return 'Repo : '+self.path_create2+' is deleted'
