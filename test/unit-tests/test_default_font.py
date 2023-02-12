import os.path
import unittest

from src.kksubs.model.domain_models import get_default_font_style


class TestDefaultFont(unittest.TestCase):

    def test_default_font(self):
        self.assertEqual(os.path.exists(get_default_font_style()), True)