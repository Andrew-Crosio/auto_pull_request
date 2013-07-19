# coding=utf-8
"""Auto pull request utilities"""
from contextlib import contextmanager, closing
from time import sleep
import httplib
import os
import subprocess
import sys

from django.conf import settings
import requests


SERVER_POLL_INTERVAL = 5
SERVER_POLL_RETRIES = 5
SERVER_TIMEOUT = 30
SERVER_TEST_URL = 'http://dubai' + settings.BASE_DOMAIN
SERVER_START_COMMANDS = ['python', 'manage.py', 'runserver', '--verbosity', '0',
                         '--settings', 'timing_settings']
VERBOSITY_DEFAULT = 1


@contextmanager
def silence_output():
    """Silence output from stdout"""
    try:
        with closing(open(os.devnull, 'w')) as null_device:
            sys.stdout = null_device
            yield
    finally:
        sys.stdout = sys.__stdout__


class BackgroundServer(object):
    def __init__(self, verbosity=VERBOSITY_DEFAULT):
        self.verbosity = verbosity
        self.process = None

    def __enter__(self):
        return self.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def start(self):
        if self.verbosity >= 1:
            print 'Spawning server...'

        self.process = subprocess.Popen(SERVER_START_COMMANDS,
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if self.verbosity >= 1:
            print 'Waiting for server...'

        spawned = False
        for _ in xrange(SERVER_POLL_RETRIES):
            try:
                response = requests.get(SERVER_TEST_URL, timeout=SERVER_TIMEOUT)
            except requests.Timeout:
                break
            else:
                if response.status_code == httplib.OK:
                    spawned = True
                    break
                else:
                    sleep(SERVER_POLL_INTERVAL)

        if not spawned:
            raise Exception('Unable to spawn server')
        else:
            if self.verbosity >= 1:
                print 'Server spawned.'

        return self.process

    def stop(self):
        if self.process:
            if self.verbosity >= 1:
                print 'Destroying server...'

            self.process.kill()
            sleep(1)
            process = subprocess.Popen(['ps', '-ef'], stdout=subprocess.PIPE)
            if process.wait():
                raise Exception()

            process_list = [filter(None, proc.split(' ')) for proc in
                            process.stdout.read().strip().split('\n')[1:]]
            for process_item in process_list:
                if ' '.join(process_item[7:]).endswith(' '.join(SERVER_START_COMMANDS)):
                    pid = process_item[1]
                    subprocess.call(['kill', '-9', str(pid)])
        else:
            print >> sys.stderr, 'Cannot stop un-started server.'
            raise Exception()
