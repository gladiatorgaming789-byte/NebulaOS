import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "desktop" / "nebula_fileops.py"
spec = importlib.util.spec_from_file_location("nebula_fileops", MODULE)
fileops = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fileops)

class FileOpsTests(unittest.TestCase):
    def test_rejects_path_traversal_names(self):
        for name in ("", ".", "..", "../escape", "folder/file", "folder\\file", "bad\x00name"):
            with self.subTest(name=repr(name)), self.assertRaises(ValueError):
                fileops.validate_name(name)
        self.assertEqual(fileops.validate_name("normal file.txt"), "normal file.txt")

    def test_copy_and_move_refuse_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); src = root / "source.txt"; src.write_text("safe")
            dst = root / "copy.txt"; fileops.copy_item(src, dst)
            self.assertEqual(dst.read_text(), "safe")
            with self.assertRaises(FileExistsError): fileops.copy_item(src, dst)
            moved = root / "moved.txt"; fileops.move_item(src, moved)
            self.assertFalse(src.exists()); self.assertEqual(moved.read_text(), "safe")
            with self.assertRaises(FileExistsError): fileops.move_item(moved, dst)

    def test_copy_and_delete_symlink_without_touching_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); target = root / "target.txt"; target.write_text("keep")
            link = root / "link.txt"; link.symlink_to(target)
            copied = root / "copied-link.txt"; fileops.copy_item(link, copied)
            self.assertTrue(copied.is_symlink())
            fileops.delete_item(link)
            self.assertTrue(target.exists()); self.assertEqual(target.read_text(), "keep")

    def test_copy_directory_preserves_nested_symlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); target = root / "target"; target.mkdir(); (target / "data").write_text("x")
            source = root / "source"; source.mkdir(); (source / "shortcut").symlink_to(target, target_is_directory=True)
            dest = root / "dest"; fileops.copy_item(source, dest)
            self.assertTrue((dest / "shortcut").is_symlink())
            self.assertEqual((dest / "shortcut").readlink(), target)

    def test_format_size(self):
        self.assertEqual(fileops.format_size(42), "42 B")
        self.assertEqual(fileops.format_size(1024), "1.0 KB")

if __name__ == "__main__": unittest.main()
