import unittest

from src.kksubs.model.converters import get_subtitle_profiles

class TestSubtitleProfileYaml(unittest.TestCase):

    def test_subtitle_profile_yaml(self):
        subtitle_profiles = get_subtitle_profiles("test/unit-tests/test_subtitle_profile_yaml.yaml")
        self.assertEqual(subtitle_profiles['default'].font_data.style, "default style")
        self.assertEqual(subtitle_profiles['red font'].font_data.color, (255, 0, 0))
        self.assertEqual(subtitle_profiles["tricky data types"].font_data.color, (255, 0, 255))