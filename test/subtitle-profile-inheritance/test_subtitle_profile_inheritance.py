import unittest

from kksubs.model.converters import get_subtitle_profiles

class TestSubtitleProfileInheritance(unittest.TestCase):

    def test_subtitle_profile_inheritance(self):

        path = "test/subtitle-profile-inheritance/subtitle_profiles.yaml"
        subtitle_profiles = get_subtitle_profiles(path)
        child_profile = subtitle_profiles["child"]
        parent_profile = subtitle_profiles["parent"]
        self.assertEqual(parent_profile.font_data.color, (255, 0, 0))
        self.assertEqual(parent_profile.font_data.size, 50)
        self.assertEqual(child_profile.font_data.color, (0, 0, 255))
        self.assertEqual(child_profile.font_data.size, 50)