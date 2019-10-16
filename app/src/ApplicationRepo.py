import datetime
import collections
import requests
from git import Repo, Git

class ApplicationRepo():
    def __init__(self,repo_path,repo_name):
        Repo.init(repo_path)
        self.repo = Repo(repo_path)
        self.repo_path = repo_path
        self.repoName = repo_name
        self.api_endpoint = "http://10.151.36.182/api/v1/user/repos"
        self.api_token = "token 1aed949ff544f998566a6d6693e11a0fb138bbb2"

    # def init_repo(self):
    #     Repo.init(self.repo_path)

    def create_gitea_repo(self):
        data_create = {
            "auto_init": True,
            "description": "string_description",

            "issue_labels": "string_labels",
            "name": self.repoName,
            "private": False
        }

        requests.post(url= self.api_endpoint, headers={'Authorization' : self.api_token}, data= data_create )



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
        show_ref = self.repo.git.show_ref(hash=7)
        show_ref = show_ref.split('\n')
        return show_ref

    def get_head(self):
        repo = self.repo
        commit = repo.head.commit
        commit = repo.git.rev_parse(commit,short=7)
        return commit

    def check_repo(self):
        head = self.get_head()
        if head in self.get_hash_branches():
            return True
        else:
            return False

    def checkout_to_branch(self):
        g = self.repo.git()
        branch_index = self.get_hash_branches().index(self.get_head())
        branch = self.get_branches()[branch_index]
        g.checkout(branch)

    def push(self):
        try:
            dateNow = datetime.datetime.now()
            self.repo.git.add('.')
            self.repo.index.commit(dateNow.strftime("%Y-%m-%d %H-%M-%S"))
            # origin = repo.remote(name='origin')
            # origin.push()
            print(self.repo)
            # print(path)
        except Exception as e:
            print("Error Occured")
            print(e)
        finally:
            print("Push completed")

        print("push function are called")

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
            for commit in reversed(commits):
                short_sha = self.repo.git.rev_parse(commit.hexsha,short=6)
                print(short_sha)
                array_commits.append(short_sha)
            result[i]=array_commits

        return result

    