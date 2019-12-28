import os
from app import var
class Repository():
    def __init__(self, repo_name):
        self.path = var.PATH
        self.name = repo_name
        
    
    def create(self):
        path_create = self.path+'/'+self.name
        os.mkdir(path_create)
        return path_create