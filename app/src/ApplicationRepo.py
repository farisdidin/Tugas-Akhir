import datetime
from git import Repo, Git

class ApplicationRepo():
    def __init__(self,repo_path,repo_name):
        Repo.init(repo_path)
        self.repo = Repo(repo_path)
        self.repo_path = repo_path
        self.repoName = repo_name

    # def init_repo(self):
    #     Repo.init(self.repo_path)

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
        num = len(self.get_branches())
        new_branch = num+'-branch'
        # initialAttributes[self.repo_name]['branches'].append(new_branch)
        g.checkout(b=new_branch)

    # def check_attribute_hash(self):
    #     global initialAttributes
    #     current = self.get_hash_branches()
    #     for i,(a,b) in enumerate(zip(initialAttributes[self.repoName]['hash_branches'],current)):
    #         if a != b:
    #             initialAttributes[self.repoName]['hash_branches'][i]=b 