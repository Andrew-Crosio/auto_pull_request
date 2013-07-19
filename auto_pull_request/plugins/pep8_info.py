# coding=utf-8
"""Auto pull request pep8 plugin"""
import subprocess

from git import Repo

from . import MASTER_BRANCH
from .base import AutoPullRequestPluginInterface, section_order
from ..nodes import NumberedList, DescriptionNode, CodeNode, NodeList, HeaderNode


class Pep8Plugin(AutoPullRequestPluginInterface):
    def _get_diff_against_master(self):
        repo = Repo('.git')
        return repo.git.diff(MASTER_BRANCH)

    def _get_pep8_compliance(self, diff):
        process = subprocess.Popen(['pep8', '--diff'], stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, errors = process.communicate(diff)
        if errors:
            raise Exception(errors)
        else:
            return filter(None, output.strip().split('\n'))

    @section_order(10)
    def section_pep8_standards_compliance(self):
        diff = self._get_diff_against_master()
        pep8_compliance = self._get_pep8_compliance(diff)
        if pep8_compliance:
            value = NodeList([
                HeaderNode('%d pep8 errors' % len(pep8_compliance), level=4),
                NumberedList([CodeNode(item) for item in pep8_compliance])
            ])
        else:
            value = DescriptionNode('100% pep8 compliant!')

        return value
