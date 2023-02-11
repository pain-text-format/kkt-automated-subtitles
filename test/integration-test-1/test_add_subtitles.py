import unittest

from src.model.data_access_services import SubtitleDataAccessService
from src.model.subtitle_services import SubtitleService


class TestAddSubtitles(unittest.TestCase):

    def test_add_subtitles_from_model(self):

        model = SubtitleDataAccessService()
        model.set_input_image_directory("test/integration-test-1/input_image_directory")
        model.set_input_text_directory("test/integration-test-1/input_text_directory")
        model.set_subtitle_profile_path("test/integration-test-1/subtitle_profiles.json")
        model.set_output_directory("test/integration-test-1/output_directory")
        textpath = model.get_textpaths()[0]

        subtitle_profiles = model.get_subtitle_profiles()

        model.default_subtitle_profile_id = "default"
        subtitles_by_textpath = model.get_subtitle_groups_by_textpath(textpath, subtitle_profiles=subtitle_profiles)
        self.assertEqual(subtitles_by_textpath["1.png"].subtitle_list[0].subtitle_profile_id, None)
        self.assertEqual(subtitles_by_textpath["1.png"].subtitle_list[0].subtitle_profile.font_data.style, "resource/fonts/Roboto/Roboto-BoldItalic.ttf")
        self.assertEqual(subtitles_by_textpath["1.png"].subtitle_list[0].subtitle_profile.font_data.color, (255, 255, 255))

        model.get_subtitle_groups()
        service = SubtitleService(model)
        service.add_subtitles()

        pass