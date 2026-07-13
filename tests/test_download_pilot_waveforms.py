import unittest

from scripts.download_pilot_waveforms import validate_product


class ValidateProductTests(unittest.TestCase):
    def test_accepts_valid_product(self) -> None:
        relative, size, digest = validate_product(
            {"path": "data/example.mseed", "bytes": 12, "md5": "a" * 32}
        )
        self.assertEqual(relative.as_posix(), "data/example.mseed")
        self.assertEqual(size, 12)
        self.assertEqual(digest, "a" * 32)

    def test_rejects_traversal(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unsafe"):
            validate_product({"path": "../escape", "bytes": 1, "md5": "a" * 32})

    def test_rejects_invalid_digest(self) -> None:
        with self.assertRaisesRegex(ValueError, "Invalid MD5"):
            validate_product({"path": "data/x", "bytes": 1, "md5": "not-md5"})


if __name__ == "__main__":
    unittest.main()
