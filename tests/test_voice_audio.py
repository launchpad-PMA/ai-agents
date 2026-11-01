import unittest

from agents.aragamago.voice_audio import elevenlabs_key_usable, telegram_voice_mime


class VoiceAudioTests(unittest.TestCase):
    def test_ogg_voice_note_is_audio_ogg(self):
        self.assertEqual(telegram_voice_mime("/tmp/note.ogg"), "audio/ogg")

    def test_other_audio_suffixes(self):
        self.assertEqual(telegram_voice_mime("clip.mp3"), "audio/mpeg")
        self.assertEqual(telegram_voice_mime("clip.wav"), "audio/wav")

    def test_key_id_is_not_usable(self):
        self.assertFalse(elevenlabs_key_usable("a" * 64))
        self.assertTrue(elevenlabs_key_usable("sk_example"))


if __name__ == "__main__":
    unittest.main()
