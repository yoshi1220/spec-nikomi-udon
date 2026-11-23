# Prepare the change directory

If the user identifies an existing change, use its branch and directory. Otherwise, when continuing the same change on `feature/<change>`, use `specs/<change>/`. If the branch already exists and only its directory is missing, create the directory. If it is unclear which change the request belongs to, confirm the target before writing.

For a new change, choose a short descriptive slug such as `export-csv` and allocate a number as follows. If it is unclear whether to start from another feature branch, confirm the starting point before creating the branch.

1. If Git remotes are configured, run `git fetch --all --prune`. If fetching fails, explain the error and say that the latest remote numbers could not be verified. Ask whether to continue with the available information or stop. Wait for the user to choose before continuing. When there are no remotes, use the local information.
2. From the target repository, run the bundled [start_change.py](../scripts/start_change.py) with Python 3 and pass the slug as its only argument. The helper uses one more than the highest number among local branches, fetched remote branches, and existing directories under `specs/`. Use the branch and directory reported by the helper. If it exits with an error, inspect the current branch and the change directory before retrying.
