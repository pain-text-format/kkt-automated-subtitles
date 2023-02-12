import unittest

from PIL import Image

from src.kksubs.model.domain_models import FontData, OutlineData, TextboxData, SubtitleProfile, Subtitle
from src.kksubs.model.subtitle_services import apply_subtitle_to_image


class TestAddSubtitles(unittest.TestCase):

    def test_add_subtitle_to_image(self):
        image = Image.open("resource/sample-images/1.png")
        subtitle_1 = Subtitle(
            subtitle_profile=SubtitleProfile(
                font_data=FontData(
                    style="resource/fonts/Roboto/Roboto-Regular.ttf",
                    color=(255, 255, 255),
                    size=50
                ),
                outline_data_1=OutlineData(
                    color=(0, 0, 0),
                    radius=5,
                    blur_strength=0
                ),
                outline_data_2=OutlineData(
                    color=(255, 0, 0),
                    radius=10,
                    blur_strength=5
                ),
                textbox_data=TextboxData(
                    alignment="left",
                    anchor_point=[-500, -300],
                    box_width=100,
                    push="down"
                )
            ),
            content=[
                "Hello world,",
                "This is the second line.",
                "This is the last line."
            ]
        )
        subtitle_2 = Subtitle(
            subtitle_profile=SubtitleProfile(
                font_data=FontData(
                    style="resource/fonts/Roboto/Roboto-Regular.ttf",
                    color=(255, 255, 255),
                    size=50
                ),
                outline_data_1=OutlineData(
                    color=(0, 0, 0),
                    radius=5,
                    blur_strength=0
                ),
                # outline_data_2=OutlineData(
                #     color=(255, 0, 0),
                #     radius=10,
                #     blur_strength=5
                # ),
                textbox_data=TextboxData(
                    alignment="right",
                    anchor_point=[-600, -300],
                    box_width=100,
                    push="down"
                )
            ),
            content=[
                "Charlie:"
            ]
        )
        image = apply_subtitle_to_image(image, subtitle_1)
        image = apply_subtitle_to_image(image, subtitle_2)
        # image.show()