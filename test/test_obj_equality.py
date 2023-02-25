import unittest

from kksubs.model.domain_models import FontData, Subtitle, SubtitleGroup, MainSubtitleProfile

class TestObjEquality(unittest.TestCase):

    def test_obj_equality(self):
        
        font_data_1 = FontData(style="123", color=[1, 2, 3])
        font_data_2 = FontData(style="123", color=[1, 2, 3])
        
        assert(font_data_1==font_data_2)
        font_data_3 = FontData(style="123", color=[1, 2, 3], size=1)
        assert(font_data_1!=font_data_3)

        profile_1 = MainSubtitleProfile(font_data=font_data_1)
        profile_2 = MainSubtitleProfile(font_data=font_data_2)
        profile_3 = MainSubtitleProfile(font_data=font_data_3)
        assert(profile_1==profile_2)
        assert(profile_1!=profile_3)

        subtitle_1 = Subtitle(subtitle_profile=profile_1, content=["hello world"])
        subtitle_2 = Subtitle(subtitle_profile=profile_2, content=["hello world"])
        subtitle_3 = Subtitle(subtitle_profile=profile_3, content=["hello world"])
        assert(subtitle_1==subtitle_2)
        assert(subtitle_1!=subtitle_3)

        subtitle_group_1 = SubtitleGroup(image_id="1.png", subtitle_list=[subtitle_1])
        subtitle_group_2 = SubtitleGroup(image_id="1.png", subtitle_list=[subtitle_2])
        subtitle_group_3 = SubtitleGroup(image_id="1.png", subtitle_list=[subtitle_3])
        assert(subtitle_group_1==subtitle_group_2)
        assert(subtitle_group_1!=subtitle_group_3)