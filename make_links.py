import json
from os import walk
import os
from os.path import relpath, join, dirname
from urllib.parse import urlencode
import subprocess

import pandas as pd

base = "/home/jovyan/workspace/flatiron-curriculum"
BASE_URL = os.getenv('BASE_URL')


with open("/home/jovyan/workspace/flatiron-utilities/course-jupyter-recipe.json") as f:
    recipe_json = f.read()
    json.loads(recipe_json)
    
    
def commit_all():
    repo = "/home/jovyan/workspace/flatiron-curriculum"
    subprocess.run("git add -A", shell=True, cwd=repo)
    subprocess.run("git commit -am sync", shell=True, cwd=repo)
    subprocess.run("git push origin main", shell=True, cwd=repo)
    
    
def find_links():
    all_data = []
    for root, directories, files in walk(base):
        for f in files:
            if not f.endswith(".ipynb"):
                continue
            notebook_path = join(root, f)
            local_path = relpath(notebook_path, base)
            print(dirname(local_path), local_path)
            uri = f"notebooks/workspace/flatiron-curriculum/{local_path}"
            frag = urlencode(dict(workspacePath=uri, apply="true", recipe=recipe_json))
            url = f"{BASE_URL}/dash/resources?" + frag
            print(local_path, url)
            all_data.append(dict(local_path=local_path, url=url))
    df = pd.DataFrame(all_data)
    df.to_csv("/home/jovyan/workspace/flatiron-curriculum/links.csv")
    
                
if __name__ == "__main__":
    # import json
    # json.loads(recipe_json)
    find_links()
    commit_all()