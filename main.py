import os
import subprocess


def remove_log_files() -> None:
    if os.path.exists('celerubeat-schedule'):
        print('Removing celerybeat-schedule...')
        os.remove('celerybeat-schedule')

    if os.path.exists('geckodriver.log'):
        print('Removing geckodriver.log...')
        os.remove('geckodriver.log')


if __name__ == '__main__':
    os.chdir('./app_scheduler')
    remove_log_files()
    subprocess.run(
        'celery -A tasks worker --beat --loglevel=WARNING -c 4 --purge',
        shell=True)
