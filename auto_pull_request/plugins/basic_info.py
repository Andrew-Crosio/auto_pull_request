# coding=utf-8
"""Auto pull request basic information plugin"""
from .base import AutoPullRequestPluginInterface, section_order
from ..helpers import get_input
from ..nodes import DescriptionNode


class BasicInfoPlugin(AutoPullRequestPluginInterface):
    @section_order(-10)
    def section_description(self):
        description = get_input('Enter Description', multiline=True)
        return DescriptionNode(description)

    @section_order(-9)
    def section_target_date(self):
        target_date = get_input('Enter Target Date')
        return DescriptionNode(target_date)

    @section_order(-8)
    def section_jira_task(self):
        jira_task = get_input('Enter JIRA Task(s)', multiline=True)
        return DescriptionNode(jira_task)

    @section_order(-7)
    def section_areas_affected(self):
        areas_affected = get_input('Enter Areas Affected', multiline=True)
        return DescriptionNode(areas_affected)

    @section_order(-6)
    def section_tested_and_reviewed_by(self):
        tested_and_reviewed_by = get_input('Enter Person Who Tested and Reviewed this')
        return DescriptionNode(tested_and_reviewed_by)

    @section_order(-5)
    def section_rejected_by_qa(self):
        rejected_by_qa = get_input('Has this been rejected by QA', default='No')
        return DescriptionNode(rejected_by_qa)
