from os.path import dirname
from datetime import datetime

def get_repo_dir():
    """ Can be called from anywhere to get project root directory """
    return dirname(dirname(__file__))

def datetime_str(dt=None):
    return datetime.strftime(dt or datetime.now(), '%m%d%Y_%H%M%S')
