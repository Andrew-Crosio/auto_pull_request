# coding=utf-8
"""Auto pull request migrations information plugin"""
import re

from git import Repo

from . import MASTER_BRANCH
from .base import AutoPullRequestPluginInterface, section_order
from ..nodes import DescriptionNode, NodeList, NumberedList, SectionNode


MIGRATION_FOLDER = 'migration_scripts'
MIGRATION_SCRIPT_MATCHER = re.compile(r'^%s/.*\.(?:py|sql|sh|rb)(?<!__init__.py)$'
                                      % MIGRATION_FOLDER)
TESTS_MATCHER = re.compile(r'(?:(?:^|[\b_./-])[Tt]est(?:[Cc]ase)?|[Tt]est[Cc]ase$)')
MIGRATION_FOLDERS = ['revert', 'rollback', 'reverse']


class MigrationsInfoPlugin(AutoPullRequestPluginInterface):
    def _get_migration_scripts(self):
        changes = []
        repo = Repo('.git')
        git_diff = repo.index.diff(MASTER_BRANCH, 'migration_scripts')
        for diff in git_diff:
            # Since we're comparing in reverse, assert file is added (new script)
            file_path = diff.a_blob.path
            if diff.deleted_file and self._is_migration_script(file_path):
                changes.append(file_path)

        return changes

    def _is_migration_script(self, file_name):
        return bool(MIGRATION_SCRIPT_MATCHER.match(file_name)
                    and not TESTS_MATCHER.match(file_name))

    def _separate_forward_and_back_scripts(self, migration_scripts):
        forward = []
        backward = []
        for script in migration_scripts:
            if any(('/%s/' % folder) in script for folder in MIGRATION_FOLDERS):
                backward.append(script)
            else:
                forward.append(script)

        return forward, backward

    @section_order(-1)
    def section_migration_scripts(self):
        migration_scripts = self._get_migration_scripts()
        if migration_scripts:
            forward, backward = self._separate_forward_and_back_scripts(migration_scripts)
            value = NodeList([
                NumberedList(forward),
                SectionNode('Rollback Scripts', NumberedList(backward), level=2)
            ])
        else:
            value = DescriptionNode('No migration scripts.')

        return value
