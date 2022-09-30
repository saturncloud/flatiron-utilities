import tempfile
import subprocess
import os
from os.path import basename


ALL_REPOS = os.getenv("ALL_REPOS")


def handle_repo(url: str):
    with tempfile.TemporaryDirectory() as tempdir:
        cmd = f"git clone {url} {tempdir}"
        print(cmd)
        subprocess.run(cmd, shell=True)
        dest = basename(url)
        dest = f"/home/jovyan/workspace/flatiron-curriculum/{dest}/"
        os.makedirs(dest, exist_ok=True)
        cmd = f"rsync -avzP --exclude .git {tempdir}/ {dest}"
        print(cmd)
        subprocess.run(cmd, shell=True)

        
def commit_all():
    repo = "/home/jovyan/workspace/flatiron-curriculum"
    subprocess.run("git add -A", shell=True, cwd=repo)
    subprocess.run("git commit -am sync", shell=True, cwd=repo)
    subprocess.run("git push origin main", shell=True, cwd=repo)
    
    
def sync_all():
    for repo in ALL_REPOS.split('\n'):
        if repo:
            handle_repo(repo)

        
if __name__ == "__main__":
    sync_all()
    commit_all()