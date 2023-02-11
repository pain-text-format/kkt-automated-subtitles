import unittest

from kksubs.model.converters import get_subtitle_groups_by_textpath, get_subtitle_profiles
from kksubs.model.domain_models import FontData


class TestModels(unittest.TestCase):

    def test_font_data_equality(self):
        self.assertEqual(FontData(style="abc"), FontData(style="abc"))

    def test_get_subtitle_groups_by_textpath(self):
        path = "test/unit-tests/test_input.json"
        subtitle_groups_by_textpath = get_subtitle_groups_by_textpath(path)
        self.assertEqual(subtitle_groups_by_textpath["1.png"].subtitle_list[0].content[0], "this is some content without a subtitle profile")
        pass

    def test_get_subtitle_profiles(self):
        path = "test/unit-tests/test_subtitle_profile.json"
        get_subtitle_profiles(path)

    pass
