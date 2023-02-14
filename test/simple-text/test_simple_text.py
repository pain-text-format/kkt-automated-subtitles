import unittest

from kksubs.kksubs import SubtitleController

class TestSimpleText(unittest.TestCase):

    def test_simple_text(self):
        controller = SubtitleController()
        controller.load_input_text_directory("test/simple-text/input-text-directory")
        controller.load_input_image_directory("test/resource/sample-images")
        controller.load_output_directory("test/simple-text/output-directory")
        controller.load_subtitle_profiles("test/simple-text/subtitle_profiles.yaml")
        controller.load_default_subtitle_profile_id()
        controller.add_subtitles()