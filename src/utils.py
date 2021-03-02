from os.path import dirname

def get_repo_dir():
    """ Can be called from anywhere to get project root directory """
    return dirname(dirname(__file__))
