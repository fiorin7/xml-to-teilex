from os import environ

def debug():
    return True if environ.get('TRANSFORM_DEBUG') else False