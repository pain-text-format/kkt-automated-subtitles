import unittest

from src.kksubs.model.subtitle_services import SubtitleDataAccessService
from src.kksubs.model.subtitle_services import SubtitleService


class TestAddSubtitles(unittest.TestCase):

    def setUp(self) -> None:
        self.model = SubtitleDataAccessService()
        self.model.set_input_image_directory("test/integration-test-2/input_image_directory")
        self.model.set_input_text_directory("test/integration-test-2/input_text_directory")
        self.model.set_subtitle_profile_path("test/integration-test-2/subtitle_profiles.json")
        self.model.set_output_directory("test/integration-test-2/output_directory")
        self.service = SubtitleService(self.model)

    def test_add_subtitles_from_model(self):
        self.service.add_subtitles()

        pass
    def test_add_subtitles_from_yaml(self):
        self.model.set_input_text_directory("test/integration-test-2/input_yaml_directory")
        self.service.add_subtitles()