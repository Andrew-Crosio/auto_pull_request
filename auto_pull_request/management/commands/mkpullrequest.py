# coding=utf-8
"""Automake pull requests"""
import sys

from django.core.management.base import NoArgsCommand

from timing_settings import AUTO_PULL_REQUEST_PLUGINS
from ...plugins.collector import PluginCollector


class Command(NoArgsCommand):
    """Runs the given command within the context of a Django environment"""
    help = 'Automatically creates a pull request.'

    def handle_noargs(self, **options):
        """Automatically create a pull request
        TODO: more info here
        """
        plugin_collector = PluginCollector(*AUTO_PULL_REQUEST_PLUGINS)
        request_node = plugin_collector.get_results()
        with open('request.txt', 'w') as request_text:
            request_node.write(request_text)

        print
        print '-' * 40
        print 'Request text (see also request.txt):'
        print '-' * 40
        print
        request_node.write(sys.stdout)
        print
