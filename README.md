# DeepCover
NFL coverage classification using deep learning on tracking data

## Setup
Create a config_personal.py modeled off of config_template.py in the `src/config` directory, filling in required information. This local file contains variables that vary for each user (e.g. data directory) and should not be pushed to the repo (it's in `.gitignore`). Any paths that are not repo-relative should derive from a variable in the config file. The `get_repo_dir` function in `src/utils.py` is useful for making repo-relative paths that are robust to directory restructuring.
