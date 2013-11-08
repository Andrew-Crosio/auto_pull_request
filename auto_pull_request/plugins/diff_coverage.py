# coding=utf-8
"""Auto pull request diffcoverage plugin"""
from contextlib import contextmanager
from contextlib import closing
from StringIO import StringIO
import subprocess

from diffcoverage.diff_coverage import diff_coverage
from django.conf import settings
from git import Repo

from . import MASTER_BRANCH
import sys
from .base import AutoPullRequestPluginInterface, section_order
from ..nodes import CodeNode


TEMPORARY_DIFF_LOCATION = '/tmp/temp.diff'


class DiffCoveragePlugin(AutoPullRequestPluginInterface):
    @contextmanager
    def _capture_stdout(self):
        with closing(StringIO()) as buffer:
            sys.stdout = sys.stderr = buffer
            try:
                yield buffer
            finally:
                sys.stdout = sys.__stdout__
                sys.stderr = sys.__stderr__

    def _write_diff_against_master(self):
        repo = Repo('.git')
        diff_value = repo.git.diff(MASTER_BRANCH)
        with open(TEMPORARY_DIFF_LOCATION, 'w') as diff_file:
            diff_file.write(diff_value)

    def _gather_test_coverage(self):
        try:
            test_command = settings.AUTO_PULL_REQUEST_TEST_COMMAND
        except AttributeError:
            test_command = 'nosetests --with-coverage --cover-branches'

        commands = test_command.split(';')
        for command in commands:
            command = command.split(' ')
            subprocess.call(command)

    def _get_diff_coverage(self):
        with self._capture_stdout() as buffer:
            diff_coverage(TEMPORARY_DIFF_LOCATION, show_all=True, sort_by='percent')
            return buffer.getvalue()

    @section_order(20)
    def section_difference_test_coverage(self):
        self._gather_test_coverage()
        self._write_diff_against_master()
        diff_value = self._get_diff_coverage()
        value = CodeNode(diff_value)

        return value
