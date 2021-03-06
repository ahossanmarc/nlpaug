import unittest
import os
import numpy as np
from dotenv import load_dotenv

import nlpaug.augmenter.audio as naa
from nlpaug.util import AudioLoader


class TestNoise(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        env_config_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '..', '..', '..', '.env'))
        load_dotenv(env_config_path)
        # https://freewavesamples.com/yamaha-v50-rock-beat-120-bpm
        cls.sample_wav_file = os.path.join(
            os.environ.get("TEST_DIR"), 'res', 'audio', 'Yamaha-V50-Rock-Beat-120bpm.wav'
        )
        # https://en.wikipedia.org/wiki/Colors_of_noise
        cls.noise_wav_file = os.path.join(
            os.environ.get("TEST_DIR"), 'res', 'audio', 'Pink_noise.ogg'
        )
        cls.audio, cls.sampling_rate = AudioLoader.load_audio(cls.sample_wav_file)
        cls.noise, cls.noise_sampling_rate = AudioLoader.load_audio(cls.noise_wav_file)

    def test_empty_input(self):
        audio = np.array([])
        aug = naa.NoiseAug()
        augmented_audio = aug.augment(audio)

        self.assertTrue(np.array_equal(audio, augmented_audio))

    def test_substitute(self):
        aug = naa.NoiseAug()
        augmented_audio = aug.augment(self.audio)

        self.assertFalse(np.array_equal(self.audio, augmented_audio))
        self.assertTrue(len(self.audio), len(augmented_audio))
        self.assertTrue(self.sampling_rate > 0)

    def test_color_noise(self):
        colors = naa.NoiseAug().model.COLOR_NOISES

        for color in colors:
            aug = naa.NoiseAug(color=color)
            augmented_audio = aug.augment(self.audio)

            self.assertFalse(np.array_equal(self.audio, augmented_audio))
            self.assertTrue(len(self.audio), len(augmented_audio))
            self.assertTrue(self.sampling_rate > 0)

    def test_background_noise(self):
        # noise > audio
        aug = naa.NoiseAug(noises=[self.noise])
        augmented_audio = aug.augment(self.audio)
        self.assertTrue(augmented_audio is not None)

        # audio > noise
        aug = naa.NoiseAug(noises=[self.audio])
        augmented_audio = aug.augment(self.noise)
        self.assertTrue(augmented_audio is not None)

    def test_coverage(self):
        zone = (0.3, 0.7)
        coverage = 0.1
        expected_aug_data_size = int(len(self.audio) * (zone[1] - zone[0]) * coverage)

        # background noise
        aug = naa.NoiseAug(zone=zone, noises=[self.noise], coverage=coverage)
        aug.model.stateless = False
        aug.augment(self.audio)

        self.assertTrue(-1 <= len(aug.model.aug_data) - expected_aug_data_size <= 1)

        # colored noise
        aug = naa.NoiseAug(zone=zone, color='pink', coverage=coverage)
        aug.model.stateless = False
        aug.augment(self.audio)

        self.assertTrue(-1 <= len(aug.model.aug_data) - expected_aug_data_size <= 1)

    def test_zone(self):
        zone = (0, 1)
        coverage = 1.
        expected_aug_data_size = int(len(self.audio) * (zone[1] - zone[0]) * coverage)

        # background noise
        aug = naa.NoiseAug(zone=zone, noises=[self.noise], coverage=coverage)
        aug.model.stateless = False
        aug.augment(self.audio)

        self.assertTrue(-1 <= len(aug.model.aug_data) - expected_aug_data_size <= 1)

        # colored noise
        aug = naa.NoiseAug(zone=zone, color='pink', coverage=coverage)
        aug.model.stateless = False
        aug.augment(self.audio)

        self.assertTrue(-1 <= len(aug.model.aug_data) - expected_aug_data_size <= 1)