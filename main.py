from clone_repos import sync_all, commit_all, sync_to_s3
from make_links import find_links, get_phases


if __name__ == "__main__":
    # all_phases = sync_all(force=True)
    # sync_to_s3(all_phases)
    phases = get_phases()
    find_links(phases)
    # commit_all()
    
