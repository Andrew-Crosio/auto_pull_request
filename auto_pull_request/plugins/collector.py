# coding=utf-8
"""Plugin collector"""
from importlib import import_module

from ..nodes import RootNode


NODE_INDEX = 1


class PluginCollector(object):
    def __init__(self, *plugins):
        self.plugin_klasses = []
        for plugin in plugins:
            module_name, klass_name = plugin.rsplit('.', 1)
            module = import_module(module_name, package='dubizzle')
            self.plugin_klasses.append(getattr(module, klass_name))

    def get_results(self):
        unordered_results = []
        for klass in self.plugin_klasses:
            plugin = klass()
            unordered_results.extend(plugin.get_sections())

        ordered_results = [item[NODE_INDEX] for item in sorted(unordered_results)]
        return RootNode(ordered_results)
