# coding=utf-8
"""Auto pull request timings information plugin"""
import httplib
import urlparse

from django.core.cache import get_cache
from django.conf import settings
from git import Repo
import requests

from timing_settings import CACHES
from . import MASTER_BRANCH
from .base import AutoPullRequestPluginInterface, section_order
from .exceptions import ResponseStatusException
from ..helpers import get_input, set_branch
from ..nodes import SectionNode, TimingNode, NodeList, DescriptionNode
from ..timings import TimingsParser, TimingsInfo
from ..server import BackgroundServer


cache = backend = get_cache(CACHES['default']['BACKEND'], **CACHES['default'])
TIMINGS_TIMEOUT = 90
TIMING_TITLES = ['Uncached', 'First Refresh', 'Second Refresh']


class TimingPlugin(AutoPullRequestPluginInterface):
    def __init__(self):
        self.base_domain = 'http://dubai' + settings.BASE_DOMAIN

    def _get_page_timings_data(self, page_url):
        info = {}
        cache.clear()
        for timing_section in TIMING_TITLES:
            try:
                response = requests.get(page_url, timeout=TIMINGS_TIMEOUT)
            except requests.Timeout:
                info[timing_section] = DescriptionNode('Response timeout after %d seconds'
                                                       % TIMINGS_TIMEOUT)
            else:
                if response.status_code != httplib.OK:
                    raise ResponseStatusException('Received status code of "%d" from "%s"'
                                                  % (response.status_code, page_url))

                info[timing_section] = TimingsParser.fromstring(response.content)

        return info

    def _get_page_timing_section_subnodes(self, after_info, before_info):
        section_subnodes = []
        for key in TimingsInfo.KEYS:
            section_subnodes.append(SectionNode(key, TimingNode(before=before_info[key],
                                                                after=after_info[key]),
                                                level=4))
        return NodeList(section_subnodes)

    def _get_pages_timings(self, pages):
        pages = [urlparse.urljoin(self.base_domain, url) for url in pages]
        pages_timings = {page: {} for page in pages}
        print
        print 'Gathering data for timings part 1 of 2...'
        with BackgroundServer():
            for page in pages:
                pages_timings[page]['after'] = self._get_page_timings_data(page)

        print
        print 'Gathering data for timings part 2 of 2...'
        with set_branch(self.repo, MASTER_BRANCH, stash=True):
            with BackgroundServer():
                for page in pages:
                    pages_timings[page]['before'] = self._get_page_timings_data(page)

        print
        page_timings_info = []
        for page_url, info in pages_timings.iteritems():
            page_info = []
            for timing_section in TIMING_TITLES:
                before_info = info['before'][timing_section]
                after_info = info['after'][timing_section]
                section_subnodes = self._get_page_timing_section_subnodes(after_info,
                                                                          before_info)
                page_info.append(SectionNode(timing_section.title(),
                                             section_subnodes, level=3))

            page_timings_info.append(
                SectionNode('"%s" Timings' % page_url, NodeList(page_info), level=2))

        return NodeList(page_timings_info)

    @section_order(2)
    def section_timings(self):
        self.repo = Repo('.git')
        pages = get_input('Enter page urls to test', multiline=True).strip()
        pages = filter(None, pages.split('\n'))
        if pages:
            value = self._get_pages_timings(pages)
        else:
            value = DescriptionNode('No page timings')

        return value
