# coding=utf-8
"""Plugin Exceptions"""
from ..exceptions import AutoPullRequestException


class PluginException(AutoPullRequestException):
    pass


class TimingPluginException(PluginException):
    pass


class ResponseStatusException(TimingPluginException):
    pass
