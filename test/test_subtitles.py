import unittest

from kksubs.model.converters import _get_subtitle_groups_from_textstring

class TestSubtitles(unittest.TestCase):

    def test_subtitles(self):
        
        content_1 = "First line"
        content_2 = "Second line\n\nSome stuff"
        test_string = f"image_id: 1.png\ncontent: {content_1}\n\ntextbox_data.alignment: left\ncontent: {content_2}"
        subtitle_groups = _get_subtitle_groups_from_textstring(test_string)
        first_image_subtitle_group = subtitle_groups['1.png']
        self.assertListEqual(first_image_subtitle_group.subtitle_list[0].content, content_1.split("\n"))
        self.assertListEqual(first_image_subtitle_group.subtitle_list[1].content, content_2.split("\n"))

    def test_grid4(self):
        test_string = "image_id: 1.png\ntextbox_data.grid4: [0, 0]\ncontent: Hello world"
        subtitle_groups = _get_subtitle_groups_from_textstring(test_string)
        subtitle_group = subtitle_groups["1.png"]
        self.assertEqual(subtitle_group.subtitle_list[0].subtitle_profile.textbox_data.grid4, (0, 0))

    pass