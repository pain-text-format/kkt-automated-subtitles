import unittest

from src.kksubs.model.data_access_services import SubtitleDataAccessService


class TestYAMLWriter(unittest.TestCase):

    def test_yaml_writer(self):

        model = SubtitleDataAccessService()
        model.set_input_image_directory("test/sample-images")
        model.generate_yaml_subtitle_template("test/unit-tests/test_yaml_written.yaml")
        pass

    def test_yaml_overwriter(self):
        model = SubtitleDataAccessService()
        model.set_input_image_directory("test/sample-images")
        model.generate_yaml_subtitle_template(
            "test/unit-tests/test_yaml_update.yaml", "test/unit-tests/existing_yaml_writer.yaml"
        )