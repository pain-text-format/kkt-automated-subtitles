import unittest

from src.kksubs.model.domain_models import FontData, OutlineData, TextboxData, SubtitleProfile


class TestSubtitleProfile(unittest.TestCase):

    def test_font_data(self):
        font_data = FontData(stroke_color='black')
        font_data.add_default()
        self.assertEqual(font_data.stroke_size, 5)

        custom_font_data = FontData(
            stroke_size=10
        )
        custom_font_data.add_default()
        self.assertEqual(custom_font_data.stroke_color, (0, 0, 0))

    def test_outline_data(self):
        outline_data = OutlineData(color='white')
        outline_data.add_default()
        self.assertEqual(outline_data.blur_strength, 0)

        custom_outline_data = OutlineData(
            color=[0, 0, 0],
            blur_strength=5
        )
        custom_outline_data.add_default()
        self.assertEqual(custom_outline_data.radius, 5)
        self.assertEqual(custom_outline_data.color, (0, 0, 0))

        local_outline_data = OutlineData(
            color="white"
        )
        self.assertEqual(local_outline_data.color, (255, 255, 255))
        local_outline_data.add_default(profile_outline_data=custom_outline_data)
        self.assertEqual(local_outline_data.color, (255, 255, 255))
        self.assertEqual(local_outline_data.blur_strength, 5)
        self.assertEqual(local_outline_data.radius, 5)

    def test_textbox_data(self):
        custom_textbox_data = TextboxData(
            alignment="left"
        )
        custom_textbox_data.add_default()
        self.assertEqual(custom_textbox_data.anchor_point, (0, 0))
        self.assertEqual(custom_textbox_data.push, "down")
        self.assertEqual(custom_textbox_data.box_width, 100)

        local_textbox_data = TextboxData(
            push="up"
        )
        local_textbox_data.add_default(custom_textbox_data)
        self.assertEqual(local_textbox_data.push, "up")
        self.assertEqual(local_textbox_data.alignment, "left")
        self.assertEqual(local_textbox_data.box_width, 100)

    def test_subtitle_profile(self):
        profile_font_data = FontData(
            style="profile style",
            color="blue"
        )
        profile_outline_data = OutlineData(
            color="black",
            radius=10
        )
        profile_textbox_data = TextboxData(
            alignment="center",
            anchor_point=[10, -10]
        )
        profile = SubtitleProfile(
            font_data=profile_font_data,
            outline_data_1=profile_outline_data,
            textbox_data=profile_textbox_data
        )
        local_font_data = FontData(
            color="white",
            size=100
        )
        local_profile = SubtitleProfile(
            font_data=local_font_data
        )
        local_profile.add_default(profile)
        self.assertEqual(local_profile.font_data.color, (255, 255, 255))
        self.assertEqual(local_profile.font_data.size, 100)
        self.assertEqual(local_profile.font_data.style, "profile style")
        self.assertEqual(local_profile.font_data.stroke_size, None)
        self.assertEqual(local_profile.outline_data_1.color, (0, 0, 0))
        self.assertEqual(local_profile.outline_data_2, None)
        self.assertEqual(local_profile.textbox_data.alignment, "center")
        self.assertEqual(local_profile.textbox_data.push, "down")
        self.assertEqual(local_profile.textbox_data.anchor_point, (10, -10))

        default_profile = SubtitleProfile()
        default_profile.add_default()
        self.assertEqual(default_profile.font_data, FontData.get_default())
        self.assertEqual(default_profile.outline_data_1, None)
        self.assertEqual(default_profile.outline_data_2, None)
        self.assertEqual(default_profile.textbox_data, TextboxData.get_default())
        self.assertEqual(default_profile.subtitle_profile_id, None)
        self.assertEqual(default_profile.background_image_path, None)
