import tempfile
from typing import List
import subprocess
import os
from io import StringIO
from os.path import basename, join, exists

import pandas as pd


ALL_REPOS = os.getenv("ALL_REPOS")


def handle_repo(url: str, phase: str, force=True):
    dest = basename(url)
    dest = f"/home/jovyan/workspace/flatiron-curriculum/{phase}/{dest}/"
    if exists(dest) and not force:
        return
    with tempfile.TemporaryDirectory() as tempdir:
        cmd = f"git clone {url} {tempdir}"
        print(cmd)
        subprocess.run(cmd, shell=True)
        os.makedirs(dest, exist_ok=True)
        cmd = f"rsync -avzP --exclude .git {tempdir}/ {dest}"
        print(cmd)
        subprocess.run(cmd, shell=True)

        
def commit_all():
    repo = "/home/jovyan/workspace/flatiron-curriculum"
    subprocess.run("git add -A", shell=True, cwd=repo)
    subprocess.run("git commit -am sync", shell=True, cwd=repo)
    subprocess.run("git push origin main", shell=True, cwd=repo)

    
def sync_to_s3(all_phases: List[str]):
    base_path = "/home/jovyan/workspace/flatiron-curriculum"
    for phase in all_phases:
        path = join(base_path, phase)
        subprocess.run(f"aws s3 sync {path} s3://flatiron-curriculum/{phase}", shell=True)
        
    
def sync_all(force=True):
    df = pd.read_csv(StringIO(ALL_REPOS))
    data = []
    for phase, repo in zip(df['Consumer Phase'].tolist(), df['Repository'].tolist()):
        repo = repo.strip()
        repo = repo.strip('/')
        phase = "".join(c for c in phase if c.isalnum())
        if repo:
            data.append((phase, repo))
    all_phases = list(set(x[0] for x in data))
    for phase, repo in data:
        handle_repo(repo, phase, force=force)
    return all_phases


if __name__ == "__main__":
    all_phases = sync_all()
    commit_all()
    sync_to_s3(all_phases)
