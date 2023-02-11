import unittest

from kksubs.model.converters import _get_subtitle_groups_from_text
from kksubs.model.domain_models import TextboxData


class TestAddSubtitleGroups(unittest.TestCase):

    def test_add_subtitle_groups(self):

        text_path = "test/unit-test-text/test_input.txt"
        subtitle_groups = _get_subtitle_groups_from_text(text_path)

        self.assertEqual(subtitle_groups["1.png"].subtitle_list[0].content, ["hello world"])
        self.assertEqual(subtitle_groups['1.png'].subtitle_list[0].subtitle_profile.font_data.style, "local style")
        self.assertEqual(subtitle_groups["2.png"].subtitle_list[0].content, ["nice to meet you", "my name is Bob"])
        self.assertEqual(subtitle_groups['2.png'].subtitle_list[1].content, ['this is second content'])
        self.assertEqual(subtitle_groups['2.png'].subtitle_list[1].subtitle_profile.textbox_data, TextboxData.get_default())
        self.assertEqual(subtitle_groups['3.png'].subtitle_list[0].content, ['this', '', 'has space between, but it will be included.'])