import shutil
import os
from app import var
from app.src.ApplicationRepo import ApplicationRepo as ar 

class Repository():
    def __init__(self, repo_name):
        self.path = var.PATH
        self.name = repo_name
        self.path_create = self.path+'/'+self.name
        
    
    def create(self):
        os.mkdir(self.path_create)
        repo = ar(self.path_create,self.name)
        repo.create_gitea_repo()
        repo.pull()
        version = repo.get_head()['message']
        return self.path_create, version

    # def remove(self):
    #     remove_path = self.path_create
    #     # shutil.rmtree(remove_path)
    #     return 'Repo : '+remove_path+' is deleted'
