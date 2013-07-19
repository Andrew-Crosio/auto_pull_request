# coding=utf-8
"""Auto pull request timings"""
from lxml import etree


TIMING_XPATH_FINDERS = {
    'sql': '//a[@class="djDebugSQLPanel"]/small/text()',
    'memcache': '//a[@class="djDebugMemcachePanel"]/small/text()',
    'redis': '//a[@class="djDebugRedisPanel"]/small/text()',
    'elapsed': '//a[@class="djDebugTimerPanel"]/small/text()'
}


class TimingsInfo(object):
    __slots__ = KEYS = TIMING_XPATH_FINDERS.keys()

    def __init__(self, **kwargs):
        for timing_key in self.KEYS:
            try:
                setattr(self, timing_key, kwargs[timing_key])
            except KeyError:
                raise TypeError('%s required key: %s' % (self.__class__.__name__,
                                                         timing_key))

    def __getitem__(self, item):
        try:
            return getattr(self, item)
        except AttributeError:
            raise KeyError(item)


class TimingsParser(object):
    @staticmethod
    def fromstring(content):
        parser = TimingsParser()
        return parser.parse(content)

    def __init__(self):
        self.parser = etree.HTMLParser()

    def parse(self, content):
        self.tree = etree.fromstring(content, self.parser)
        parsed_options = {}
        for key, xpath_finder in TIMING_XPATH_FINDERS.iteritems():
            try:
                parsed_options[key] = self.tree.xpath(xpath_finder)[0]
            except IndexError:
                raise Exception(
                    'Unable to find xpath (are you sure timings server is up?')

        return TimingsInfo(**parsed_options)
