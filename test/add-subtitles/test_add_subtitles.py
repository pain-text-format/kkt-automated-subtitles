import unittest

from kksubs.kksubs import SubtitleController


class TestAddSubtitles(unittest.TestCase):

    def test_add_subtitles(self):
        controller = SubtitleController()
        controller.load_configs("test/add-subtitles/config.yaml")
        controller.load_default_subtitle_profile_id("default")
        controller.add_subtitles()