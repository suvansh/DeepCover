try:
    from .config_personal import *
    print(f'Using personal config for user: {user} and data_dir: {data_dir}')
except ImportError:
    from .config_template import *
    print('Using template config')
