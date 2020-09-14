import os
import subprocess


if __name__ == '__main__':
    os.chdir('./app_scheduler')
    subprocess.run('celery -A tasks worker --beat --loglevel=WARNING',
                   shell=True)
