import argparse
import ctypes
import sys
import unittest
from unittest.mock import patch

from PIL import Image

from experiments.game_io.probe import WindowsGame, valid_duration
from experiments.vision.match import demo_images, locate


class VisionTests(unittest.TestCase):
    def test_detects_inserted_template_in_full_image_and_roi(self):
        scene, template = demo_images()
        for roi in (None, (40, 20, 90, 70)):
            with self.subTest(roi=roi):
                result = locate(scene, template, roi=roi)
                self.assertTrue(result["found"])
                self.assertEqual(result["bbox"], [53, 37, 7, 9])

    def test_absent_template_does_not_produce_coordinates(self):
        _, template = demo_images()
        result = locate(Image.new("RGB", (32, 32)), template)
        self.assertFalse(result["found"])
        self.assertIsNone(result["bbox"])

    def test_invalid_regions_and_uninformative_templates_are_rejected(self):
        scene, template = demo_images()
        for roi in ((-1, 0, 20, 20), (0, 0, 2, 2)):
            with self.assertRaises(ValueError):
                locate(scene, template, roi=roi)
        with self.assertRaises(ValueError):
            locate(scene, Image.new("RGB", (3, 3)))
        with self.assertRaises(ValueError):
            locate(scene, Image.new("RGB", (3, 3), "red"))


class GameTests(unittest.TestCase):
    @unittest.skipUnless(sys.platform == "win32", "Structure Win32 vérifiée sous Windows")
    def test_windows_input_layout(self):
        game = WindowsGame("brotato")
        expected = 40 if ctypes.sizeof(ctypes.c_void_p) == 8 else 28
        self.assertEqual(ctypes.sizeof(game.Input), expected)

    def test_duration_is_bounded(self):
        self.assertEqual(valid_duration("0.2"), 0.2)
        for invalid in ("0", "-1", "1", "nan", "inf"):
            with self.assertRaises(argparse.ArgumentTypeError):
                valid_duration(invalid)

    def test_key_is_released_when_focus_is_lost(self):
        # Aucun appel Win32 : vérifier uniquement le contrat de libération.
        game = object.__new__(WindowsGame)
        with patch.object(game, "focused", side_effect=[123, RuntimeError("focus perdu")]), \
             patch.object(game, "key") as key:
            game.api = type("API", (), {"GetAsyncKeyState": lambda _, vk: 0})()
            with self.assertRaises(RuntimeError):
                game.pulse("right", 0.2, 123)
            self.assertEqual(key.call_count, 2)
            key.assert_called_with(0x27, release=True)


if __name__ == "__main__":
    unittest.main()
