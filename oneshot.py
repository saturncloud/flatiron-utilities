import click

from clone_repos import handle_repo, sync_to_s3, commit_all
from make_links import make_just_phase_link


@click.command()
@click.argument('repo')
@click.argument('phase')
@click.argument('base_url')
@click.argument('suffix')
def run(repo: str, phase: str, base_url: str, suffix: str):
    handle_repo(repo, phase)
    sync_to_s3([phase])
    commit_all()
    url = make_just_phase_link(phase, "/home/jovyan/workspace/flatiron-utilities/recipes/recipe.json", base_url, suffix)
    print(url)

if __name__ == "__main__":
    run()