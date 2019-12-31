import datetime
import collections
import requests
from git import Repo, Git
from app import var

class ApplicationRepo():
    def __init__(self,repo_path,repo_name):
        Repo.init(repo_path)
        self.repo = Repo(repo_path)
        self.repo_path = repo_path
        self.repoName = repo_name
        self.api_endpoint = "http://localhost:3000/api/v1/user/repos"
        self.api_token = var.API_TOKEN
        # self.api_token = "token 5b297d2d0f6e7c6f5d7a7a8de53a776ae008c386"
        self.repo_url = var.URL_GITEA+self.repoName+".git"
        # self.repo_url = "http://didin:didin23@localhost:3000/didin/"+self.repoName+".git"

    # def init_repo(self):
    #     Repo.init(self.repo_path)

    def create_gitea_repo(self):
        data_create = {
            "auto_init": True,
            "description": "Readme for device "+ self.repoName,
            "name": self.repoName,
            "private": False
        }

        requests.post(url= self.api_endpoint, headers={'Authorization' : self.api_token}, data= data_create )
        g=self.repo.git
        g.remote('add', 'origin', self.repo_url)

    def remove_gitea_repo(self):
        endpoint = 'http://localhost:3000/api/v1/repos/faris/'+self.repoName
        requests.delete(url=endpoint, headers={'Authorization' : self.api_token} )

    def get_branches(self):
        branch = self.repo.git.branch()
        branch = branch.replace('*','')
        branch = branch.replace(' ','')
        branch_split = branch.split('\n')
        indices = [i for i, s in enumerate(branch_split) if 'HEAD' in s]
        # print(indices)
        if indices:
            del branch_split[indices[0]]
        return branch_split

    def get_hash_branches(self):
        show_ref = self.repo.git.show_ref(hash=10)
        show_ref = show_ref.split('\n')
        return show_ref

    def get_head(self):
        repo = self.repo
        commit = repo.head.commit
        message = repo.head.commit.message
        commit = repo.git.rev_parse(commit,short=10)
        result = collections.defaultdict(dict)
        result["commit"]=commit
        result["message"]=message
        return result

    def check_repo(self):
        head = self.get_head()['commit']
        if head in self.get_hash_branches():
            return True
        else:
            return False

    def checkout_to_branch(self):
        g = self.repo.git()
        branch_index = self.get_hash_branches().index(self.get_head()['commit'])
        branch = self.get_branches()[branch_index]
        g.checkout(branch)

    def push(self):
        try:
            dateNow = datetime.datetime.now()
            self.repo.git.add('.')
            self.repo.index.commit(dateNow.strftime("%Y-%m-%d %H-%M-%S"))
            origin = self.repo.remote(name='origin')
            current_commit = self.get_head()['commit']
            index_branch = self.get_hash_branches().index(current_commit)
            current_branch = self.get_branches()[index_branch]
            
            origin.push(current_branch)
            print(self.repo)
            # print(path)
        except Exception as e:
            print("Error Occured")
            print(e)
        finally:
            print("Push completed")

        print("push function are called")

    def pull(self):
        g=self.repo.git
        # g.remote('add', 'origin', self.repo_url)
        self.repo.git.pull('origin', 'master')

    def create_branch(self):
        g = self.repo.git
        num = str(len(self.get_branches()))
        new_branch = num+'-branch'
        # initialAttributes[self.repo_name]['branches'].append(new_branch)
        g.checkout(b=new_branch)

    def checkout(self, commit):
        g = self.repo.git
        g.checkout(commit)

    def get_log(self):
        g = self.repo.git
        return g.log(all=True, oneline=True, graph=True)

    def get_list_commits(self):
        branches = self.get_branches()
        result = collections.defaultdict(dict)
        for i in branches:
            commits = list(self.repo.iter_commits(i))
            print(i)
            array_commits = []
            result[i] = []
            for commit in reversed(commits):
                short_sha = self.repo.git.rev_parse(commit.hexsha,short=10)
                message = commit.message
                if short_sha == self.get_head()['commit']:
                    result[i].append([short_sha, message, 'HEAD'])
                else:
                    result[i].append([short_sha, message])

                print(short_sha)
                array_commits.append(short_sha+ ' ' +message)
            # result[i]=array_commits

        return result,branches

    