from clone_repos import sync_all, commit_all, sync_to_s3
from make_links import find_links


if __name__ == "__main__":
    sync_all()
    find_links()
    commit_all()
    sync_to_s3()