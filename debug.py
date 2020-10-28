from os import environ

def debug():
    return False if environ.get('TRANSFORM_NO_DEBUG') else True