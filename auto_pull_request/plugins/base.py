# coding=utf-8
"""Auto pull request plugin base"""
import abc
import types

from ..nodes import SectionNode, NodeList


DEFAULT_ORDERING_POSITION = 1
SECTION_METHOD_PREFIX = 'section_'
SECTION_ORDER_ATTRIBUTE = 'section_order'


def section_order(pos):
    def _section_order_decorator(func):
        setattr(func, SECTION_ORDER_ATTRIBUTE, pos)
        return func

    return _section_order_decorator


class AutoPullRequestPluginInterface(object):
    __metaclass__ = abc.ABCMeta

    def get_section_commands(self):
        for attr in dir(self):
            if (attr.startswith(SECTION_METHOD_PREFIX)
                    and isinstance(getattr(self, attr), types.MethodType)):
                yield attr

    def get_sections(self):
        sections = []
        for command_name in self.get_section_commands():
            section_title = ' '.join(part.title() for part in command_name.split('_')[1:])
            method = getattr(self, command_name)
            ordering = getattr(method, SECTION_ORDER_ATTRIBUTE, DEFAULT_ORDERING_POSITION)
            command_results = method()
            if command_results:
                sections.append((ordering, SectionNode(section_title, command_results)))

        if not sections:
            raise Exception('No sections for plugin: %s' % self.__class__.__name__)
        elif len(sections) > 1:
            return sections
        else:
            return sections
