from utils.tenxun_cos import create_bucket
from utils.email_send import random_str

def create_buckret_d(func):
    def wrapper(*args, **kwargs):
        bucket = str(random_str(12))
        result = func(*args, **kwargs, bucket=bucket)
        print()
        create_bucket(bucket)
        return result
    return wrapper