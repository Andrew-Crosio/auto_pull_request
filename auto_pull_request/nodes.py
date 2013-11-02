# coding=utf-8
"""Automatic pull request text nodes"""
import abc


class Node(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_text(self):
        raise NotImplementedError()

    def __repr__(self):
        return '<%s: "%s">' % (self.__class__.__name__, self.get_text())

    def __str__(self):
        return self.get_text()

    def __unicode__(self):
        return unicode(self.get_text())


class TextNode(Node):
    def __init__(self, text):
        assert isinstance(text, basestring) or hasattr(text, '__str__')

        self.text = text

    def get_text(self):
        return self.text

    def __radd__(self, other):
        return '%s %s' % (str(other), self.get_text())

    def __add__(self, other):
        return '%s %s' % (self.get_text(), str(other))


class DescriptionNode(TextNode):
    pass


class BoldNode(TextNode):
    def get_text(self):
        return '**%s**' % super(BoldNode, self).get_text()


class CodeNode(TextNode):
    def get_text(self):
        return '```%s```' % super(CodeNode, self).get_text()


class HeaderNode(TextNode):
    def __init__(self, text, level=1):
        assert level >= 1

        self.level = level
        super(HeaderNode, self).__init__(text)

    def get_text(self):
        return '\n%s %s' % ('#' * self.level, super(HeaderNode, self).get_text())


class BulletPointNode(TextNode):
    def get_text(self):
        return '* %s' % super(BulletPointNode, self).get_text()


class NodeList(Node):
    def __init__(self, nodes):
        self.nodes = nodes

    def get_text(self):
        return '\n'.join(node.get_text() for node in self.nodes)


class NumberedList(NodeList):
    def _get_numbered_items(self):
        for pos, node in enumerate(self.nodes):
            yield '%d. %s' % (pos, node)

    def get_text(self):
        return '\n'.join(self._get_numbered_items())


class RootNode(NodeList):
    def write(self, stream):
        stream.write(self.get_text())


class SectionNode(NodeList):
    def __init__(self, title, body, level=1):
        super(SectionNode, self).__init__([HeaderNode(title, level=level), body])


class TimingNode(NodeList):
    def __init__(self, before, after):
        super(TimingNode, self).__init__([
            BulletPointNode(BoldNode('Before:') + CodeNode(before)),
            BulletPointNode(BoldNode('After:') + CodeNode(after))
        ])
