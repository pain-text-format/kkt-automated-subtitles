import unittest

from kksubs.model.converters import get_subtitle_profiles

class TestOrbits(unittest.TestCase):

    def test_orbits(self):
        subtitle_profiles = get_subtitle_profiles("test\orbits\subtitle_profiles.yaml")
        self.assertEqual(subtitle_profiles["default"].orbits[0].subtitle_profile_id, "orbit")
        self.assertEqual(subtitle_profiles["default"].orbits[0].font_data.color, (255, 0, 0))
        self.assertEqual(subtitle_profiles["default"].orbits[0].font_data.size, 123)