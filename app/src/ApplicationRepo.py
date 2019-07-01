from git import Repo, Git

class ApplicationRepo():
    def __init__(self,repo_path,repo_name):
        self.repo = Repo(repo_path)
        
        self.repoName = repo_name

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

    # def check_attribute_hash(self):
    #     global initialAttributes
    #     current = self.get_hash_branches()
    #     for i,(a,b) in enumerate(zip(initialAttributes[self.repoName]['hash_branches'],current)):
    #         if a != b:
    #             initialAttributes[self.repoName]['hash_branches'][i]=b 