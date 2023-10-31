from functools import cache
import json
from typing import Dict, List
from os import walk
import os
from os.path import relpath, join, dirname
from urllib.parse import urlencode
import subprocess
from io import StringIO

import pandas as pd

from clone_repos import sync_all, sync_to_s3


ALL_REPOS = os.getenv("ALL_REPOS")
course_base = "/home/jovyan/workspace/flatiron-curriculum"
BASE_URL = os.getenv('BASE_URL')

urls = {
    "consumer": "https://app.flatironschool.saturnenterprise.io",
    "enterprise": "https://app.fisenterprise.saturnenterprise.io",
    "moringa": "https://app.moringa.saturnenterprise.io",
    "academyxi": "https://app.academyxi.saturnenterprise.io",
    "vanguard": "https://app.vanguarddigital.saturnenterprise.io",
}
default_recipe_path = "/home/jovyan/workspace/flatiron-utilities/recipes/recipe.json"
recipe_paths = {
    "moringa": "/home/jovyan/workspace/flatiron-utilities/recipes/recipe_moringa.json"
}


@cache
def get_recipe_json(installation: str, phase: str) -> str:
    recipe_path = recipe_paths.get(installation, None)
    if recipe_path is None:
        recipe_path = default_recipe_path
    with open(recipe_path, "r") as f:
        recipe_json = f.read()
    recipe_json = recipe_json.replace('{phase_lowered}', phase.lower()).replace('{phase}', phase)
    return recipe_json


def commit_all():
    repo = "/home/jovyan/workspace/flatiron-curriculum"
    subprocess.run("git add -A", shell=True, cwd=repo)
    subprocess.run("git commit -am sync", shell=True, cwd=repo)
    subprocess.run("git push origin main", shell=True, cwd=repo)

    
def make_just_phase_link(phase: str, recipe_path: str, base_url: str, suffix: str) -> str:
    with open(recipe_path) as f:
        recipe_json = f.read()
    recipe_json = recipe_json.replace('{phase_lowered}', phase.lower()).replace('{phase}', phase)
    all_data = []
    uri = f"tree/workspace/flatiron-curriculum/{phase}/{suffix}"
    frag = urlencode(dict(workspacePath=uri, apply="true", recipe=recipe_json))
    url = f"{base_url}/dash/resources?" + frag
    return url


def make_links(phase: str, phase_base: str) -> List[Dict]:
    all_data = []
    for root, directories, files in walk(phase_base):
        for f in files:
            if not f.endswith(".ipynb"):
                continue
            notebook_path = join(root, f)
            local_path = relpath(notebook_path, course_base)
            print(dirname(local_path), local_path)
            uri = f"notebooks/workspace/flatiron-curriculum/{local_path}"
            data = dict(local_path=local_path)
            for k, v in urls.items():
                recipe_json = get_recipe_json(k, phase)
                frag = urlencode(dict(workspacePath=uri, apply="true", recipe=recipe_json))
                url = f"{v}/dash/resources?" + frag
                data[k] = url
            all_data.append(data)
    all_data = sorted(all_data, key = lambda x: x['local_path'])
    return all_data


def find_links(phases: List[str]):
    all_data = []
    by_phase = {}
    for phase in phases:
        data = make_links(phase, f"{course_base}/{phase}")
        all_data.extend(data)
        by_phase[phase] = data
            
    df = pd.DataFrame(all_data)
    df = df.sort_values('local_path')
    df.to_csv("/home/jovyan/workspace/flatiron-curriculum/links.csv", index=False)

    keys = sorted(urls)
    
    for phase in phases:
        data = by_phase[phase]
        phase_lower = phase.lower()
        with open(f"/home/jovyan/workspace/flatiron-curriculum/{phase_lower}.md", "w+") as f:
            for d in data:
                f.write(f"__{d['local_path']}__ \n")
                for k in keys:
                    f.write(f"* [{k}]({d[k]})\n")
                f.write("\n")
                
                
def get_phases():
    df = pd.read_csv(StringIO(ALL_REPOS))
    data = []
    for phase, repo in zip(df['Consumer Phase'].tolist(), df['Repository'].tolist()):
        phase = "".join(c for c in phase if c.isalnum())
        if repo:
            data.append((phase, repo))
    all_phases = list(set(x[0] for x in data))
    return all_phases

                
if __name__ == "__main__":
    # import json
    # json.loads(recipe_json)
    phases = get_phases()
    find_links(phases)
    commit_all()
    
