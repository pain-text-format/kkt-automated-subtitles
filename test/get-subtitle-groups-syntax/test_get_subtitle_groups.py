import unittest

from src.kksubs.model.data_access_services import SubtitleDataAccessService

class TestGetSubtitleGroups(unittest.TestCase):


    def test_get_subtitle_groups(self):
        model = SubtitleDataAccessService()
        model.set_subtitle_profile_path("test/get-subtitle-groups-syntax/subtitle_profiles.yaml")
        model.set_default_subtitle_profile_id("default")
        subtitle_groups = model.get_subtitle_groups_by_textpath("test/get-subtitle-groups-syntax/example.txt")

        self.assertListEqual(subtitle_groups['1.png'].subtitle_list[0].content, ['This is text for the first image.', 'Hello: world'])
        self.assertListEqual(subtitle_groups['2.png'].subtitle_list[0].content, ['This is text for the second image.', 'This is a second line.'])
        self.assertListEqual(subtitle_groups['3.png'].subtitle_list[0].content, ['This is text for the third image.', '', 'After a space, this line will also be added.'])
        self.assertListEqual(subtitle_groups['3.png'].subtitle_list[1].content, [])
        self.assertListEqual(subtitle_groups['4.png'].subtitle_list[0].content, ['This is text for the last image. The empty space before image_id is ignored.'])

        self.assertEqual(subtitle_groups['1.png'].subtitle_list[0].subtitle_profile.textbox_data.anchor_point, (0, -300))
        self.assertEqual(subtitle_groups['3.png'].subtitle_list[1].subtitle_profile.textbox_data.anchor_point, (0, 200))