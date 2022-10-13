import tempfile
import subprocess
import os
from io import StringIO
from os.path import basename

import pandas as pd


ALL_REPOS = os.getenv("ALL_REPOS")


def handle_repo(url: str, phase: str):
    with tempfile.TemporaryDirectory() as tempdir:
        phase = "".join(c for c in phase if c.isalnum())
        cmd = f"git clone {url} {tempdir}"
        print(cmd)
        subprocess.run(cmd, shell=True)
        dest = basename(url)
        dest = f"/home/jovyan/workspace/flatiron-curriculum/{phase}/{dest}/"
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
    df = pd.read_csv(StringIO(ALL_REPOS))
    for phase, repo in zip(df['Consumer Phase'].tolist(), df['Repository'].tolist()):
        if repo and "deloitte" not in repo:
            handle_repo(repo, phase)

        
if __name__ == "__main__":
    sync_all()
    commit_all()