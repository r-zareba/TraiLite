import os
import subprocess

print(os.getcwd())
os.chdir('./app_scheduler')
print(os.getcwd())


subprocess.run('celery -A tasks worker --beat --loglevel=info', shell=True)


