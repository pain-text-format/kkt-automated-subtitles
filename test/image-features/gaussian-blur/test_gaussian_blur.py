import unittest

from kksubs.kksubs import SubtitleController

class TestGaussianBlur(unittest.TestCase):

    def test_gaussian_blur(self):

        controller = SubtitleController()
        controller.load_input_text_directory("test/image-features/gaussian-blur/input-text-directory")
        controller.load_input_image_directory("test/resource/sample-images")
        controller.load_output_directory("test/image-features/gaussian-blur/output-directory")
        controller.load_subtitle_profiles("test/image-features/gaussian-blur/subtitle_profiles.yaml")
        controller.load_default_subtitle_profile_id("default")
        controller.add_subtitles()