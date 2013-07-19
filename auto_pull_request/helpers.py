# coding=utf-8
"""Auto pull request helpers"""
from contextlib import contextmanager
from git import GitCommandError

from .exceptions import GitException


@contextmanager
def set_branch(repo, branch_name, stash=False):
    original_branch_name = repo.head.ref.name
    if stash and repo.is_dirty():
        repo.git.stash()

    try:
        branch = getattr(repo.heads, branch_name)
    except AttributeError:
        raise GitException('Branch "%s" does not exist' % branch_name)
    else:
        try:
            branch.checkout()
            yield
        finally:
            original_branch = getattr(repo.heads, original_branch_name)
            original_branch.checkout()
            if stash and repo.is_dirty:
                try:
                    repo.git.stash('pop')
                except GitCommandError:
                    # TODO: determine why this is happening
                    pass


def get_input(message, multiline=False, default=''):
    if default:
        message = '%s [default: %s]' % (message, default)

    if multiline:
        user_input = []
        print '%s (blank line to end):' % message
        while True:
            next_input = raw_input().strip()
            if next_input:
                user_input.append(next_input)
            else:
                break

        user_input = '\n'.join(user_input)
    else:
        user_input = raw_input('%s: ' % message).strip()

    return user_input or default
