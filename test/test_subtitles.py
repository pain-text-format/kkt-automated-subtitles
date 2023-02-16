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

    def test_layer_data(self):

        layer_data = "layer_data.background_path: background path\n\nlayer_data.foreground_path: foreground path"
        content = "abcde"
        test_string = f"image_id: 2.png\n{layer_data}\ncontent:{content}"
        subtitle_groups = _get_subtitle_groups_from_textstring(test_string)
        subtitle_group = subtitle_groups["2.png"]
        self.assertListEqual(subtitle_group.subtitle_list[0].content, content.split("\n"))
        self.assertEqual(subtitle_group.subtitle_list[0].subtitle_profile.layer_data.background_path, "background path")
        self.assertEqual(subtitle_group.subtitle_list[0].subtitle_profile.layer_data.foreground_path, "foreground path")
        self.assertEqual(subtitle_group.subtitle_list[0].subtitle_profile.layer_data.blur_strength, None)
        self.assertEqual(subtitle_group.subtitle_list[0].subtitle_profile.layer_data.brightness, None)

    pass