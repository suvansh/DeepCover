from os.path import dirname
from datetime import datetime
import json
from collections import OrderedDict
import itertools


def get_repo_dir():
    """ Can be called from anywhere to get project root directory """
    return dirname(dirname(__file__))

def datetime_str(dt=None):
    return datetime.strftime(dt or datetime.now(), '%m%d%Y_%H%M%S')

def logger(msg, file=None, log_to_file=False):
    assert not (log_to_file and file is None)
    print(msg)
    print(msg, file=file)

def jsonify_helper(obj):
    primitives = (str, int, bool, float)
    if isinstance(obj, primitives):
        return obj
    elif isinstance(obj, list):
        return [jsonify_helper(item) for item in v]
    elif isinstance(obj, dict):
        return {k: jsonify_helper(v) for k, v in obj.items()}
    else:
        return 'OBJ|' + repr(obj) + '|' + repr(obj.__dict__)

def jsonify(obj, out_file=None, *args, **kwargs):
    """
    :param obj: the thing to jsonify
    :param out_file: file object to write json to. if None, returns string.
    :param args, kwargs: forwarded to json.dump or dumps
    :returns if OUT_FILE is None, returns json string representing OBJ. else returns None
    """
    def jsonify_helper(obj):
        primitives = (str, int, bool, float)
        if isinstance(obj, primitives):
            return obj
        elif isinstance(obj, list):
            return [jsonify_helper(item) for item in v]
        elif isinstance(obj, dict):
            return {k: jsonify_helper(v) for k, v in obj.items()}
        else:
            return 'OBJ|' + str(obj) + '|' + str(obj.__dict__)

    jsonify_ready_obj = jsonify_helper(obj)
    if out_file is None:
        return json.dumps(jsonify_ready_obj, *args, **kwargs)
    else:
        json.dump(jsonify_ready_obj, out_file, *args, **kwargs)
    
def sweep(params):
	"""
	:param params: dict mapping parameter names to a list containing all values that parameter should take on. eg {'learning_rate': [1e-3, 1e-4, 1e-5], 'num_layers': [16, 32]}
	:returns Cartesian product of params in the form of a list of dicts mapping parameter names to values from the corresponding list
	"""
	od = OrderedDict(params)  # so keys() and values() reliably return in same order
	return list(dict(zip(od.keys(), assignment)) for assignment in itertools.product(*od.values()))
 
