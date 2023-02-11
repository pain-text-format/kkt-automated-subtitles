import unittest

import yaml

from kksubs.model.converters import _get_subtitle_groups_from_dict


class TestReadYaml(unittest.TestCase):

    def test_read_yaml(self):
        path = "test/unit-tests/test_yaml_input.yaml"
        with open(path, "r", encoding="utf-8") as reader:
            content = yaml.safe_load(reader)
        result = _get_subtitle_groups_from_dict(content)
        self.assertEqual(result["2.png"].subtitle_list[0].subtitle_profile.font_data.color, (0, 1, 2))
        self.assertEqual(result["3.png"].subtitle_list[1].content[0], "this is another line somewhere else.")