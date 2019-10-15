"""
Functions related to interacting with github
"""


def push_origin_master(path_repo_dir, message):
    """
    commit update message and push updates to origin master
    
    Arguments:
    ----------
        path_repo_dir: path to directory where repo is
        message: commit message
        
    """
    
    from git import Repo
    
    repo = Repo(path_repo_dir)
    repo.git.add('.')
    try:
        repo.git.commit('-m', message)
    except Exception as e:
        print(e)
    repo.git.push('origin', 'master')