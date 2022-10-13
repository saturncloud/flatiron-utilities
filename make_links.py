import json
from typing import Dict, List
from os import walk
import os
from os.path import relpath, join, dirname
from urllib.parse import urlencode
import subprocess

import pandas as pd

from clone_repos import sync_all, sync_to_s3


course_base = "/home/jovyan/workspace/flatiron-curriculum"
BASE_URL = os.getenv('BASE_URL')

    
def commit_all():
    repo = "/home/jovyan/workspace/flatiron-curriculum"
    subprocess.run("git add -A", shell=True, cwd=repo)
    subprocess.run("git commit -am sync", shell=True, cwd=repo)
    subprocess.run("git push origin main", shell=True, cwd=repo)
    
    
def make_links(phase_base: str, recipe_path: str) -> List[Dict]:
    with open(recipe_path) as f:
        recipe_json = f.read()
        
    all_data = []
    for root, directories, files in walk(phase_base):
        for f in files:
            if not f.endswith(".ipynb"):
                continue
            notebook_path = join(root, f)
            local_path = relpath(notebook_path, course_base)
            print(dirname(local_path), local_path)
            uri = f"notebooks/workspace/flatiron-curriculum/{local_path}"
            frag = urlencode(dict(workspacePath=uri, apply="true", recipe=recipe_json))
            url = f"{BASE_URL}/dash/resources?" + frag
            print(local_path, url)
            all_data.append(dict(local_path=local_path, url=url))
    return all_data


def find_links():
    all_data = []
    all_data += make_links(f"{course_base}/Prep", "/home/jovyan/workspace/flatiron-utilities/recipes/prep-recipe.json")
    all_data += make_links(f"{course_base}/Phase1", "/home/jovyan/workspace/flatiron-utilities/recipes/phase1-recipe.json")
    all_data += make_links(f"{course_base}/Phase2", "/home/jovyan/workspace/flatiron-utilities/recipes/phase2-recipe.json")
    all_data += make_links(f"{course_base}/Phase3", "/home/jovyan/workspace/flatiron-utilities/recipes/phase3-recipe.json")
    all_data += make_links(f"{course_base}/Phase4", "/home/jovyan/workspace/flatiron-utilities/recipes/phase4-recipe.json")    
    df = pd.DataFrame(all_data)
    df.to_csv("/home/jovyan/workspace/flatiron-curriculum/links.csv")
    with open("/home/jovyan/workspace/flatiron-curriculum/links.md", "w+") as f:
        for d in all_data:
            local_path = d['local_path']
            link = d['url']
            f.write(f"* [{local_path}]({link})\n")
    
                
if __name__ == "__main__":
    # import json
    # json.loads(recipe_json)
    #sync_all()
    find_links()
    commit_all()
    #sync_to_s3()