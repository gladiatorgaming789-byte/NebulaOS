import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

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
            root = Path(tmp)
            src = root / "source.txt"
            src.write_text("safe")
            dst = root / "copy.txt"
            fileops.copy_item(src, dst)
            self.assertEqual(dst.read_text(), "safe")
            with self.assertRaises(FileExistsError):
                fileops.copy_item(src, dst)
            moved = root / "moved.txt"
            fileops.move_item(src, moved)
            self.assertFalse(src.exists())
            self.assertEqual(moved.read_text(), "safe")
            with self.assertRaises(FileExistsError):
                fileops.move_item(moved, dst)

    def test_copy_and_delete_symlink_without_touching_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "target.txt"
            target.write_text("keep")
            link = root / "link.txt"
            link.symlink_to(target)
            copied = root / "copied-link.txt"
            fileops.copy_item(link, copied)
            self.assertTrue(copied.is_symlink())
            fileops.delete_item(link)
            self.assertTrue(target.exists())
            self.assertEqual(target.read_text(), "keep")

    def test_copy_directory_preserves_nested_symlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "target"
            target.mkdir()
            (target / "data").write_text("x")
            source = root / "source"
            source.mkdir()
            (source / "shortcut").symlink_to(target, target_is_directory=True)
            dest = root / "dest"
            fileops.copy_item(source, dest)
            self.assertTrue((dest / "shortcut").is_symlink())
            self.assertEqual((dest / "shortcut").readlink(), target)

    def test_copy_and_move_reject_directory_into_itself_or_descendant(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source"
            source.mkdir()
            (source / "data.txt").write_text("finite")
            for operation in (fileops.copy_item, fileops.move_item):
                with self.subTest(operation=operation.__name__), self.assertRaises(ValueError):
                    operation(source, source / "nested" / "destination")
            self.assertEqual((source / "data.txt").read_text(), "finite")
            self.assertFalse((source / "nested").exists())

    def test_existing_symlink_destination_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.txt"
            source.write_text("source")
            target = root / "target.txt"
            target.write_text("preserve")
            destination = root / "destination.txt"
            destination.symlink_to(target)
            for operation in (fileops.copy_item, fileops.move_item):
                with self.subTest(operation=operation.__name__), self.assertRaises(FileExistsError):
                    operation(source, destination)
            self.assertEqual(target.read_text(), "preserve")
            self.assertEqual(source.read_text(), "source")

    def test_copy_file_uses_atomic_no_overwrite_publish(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.txt"
            source.write_text("new content")
            destination = root / "destination.txt"
            fileops.copy_item(source, destination)
            self.assertEqual(destination.read_text(), "new content")
            self.assertFalse(list(root.glob("*.copy-tmp")))


    def test_cross_filesystem_move_fallback_copies_then_removes_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.txt"
            source.write_text("move safely")
            destination = root / "destination.txt"
            with patch.object(fileops, "_rename_no_replace", return_value=False):
                fileops.move_item(source, destination)
            self.assertFalse(source.exists())
            self.assertEqual(destination.read_text(), "move safely")

    def test_copy_permission_error_preserves_source_and_cleans_temporary_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.txt"
            source.write_text("keep source")
            destination = root / "destination.txt"
            with patch.object(fileops.shutil, "copy2", side_effect=PermissionError("denied")):
                with self.assertRaises(PermissionError):
                    fileops.copy_item(source, destination)
            self.assertTrue(source.exists())
            self.assertFalse(destination.exists())
            self.assertEqual(source.read_text(), "keep source")
            self.assertFalse(list(root.glob(".*.copy-tmp")))

    def test_copy_race_does_not_overwrite_destination_created_after_initial_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.txt"
            source.write_text("source")
            destination = root / "destination.txt"

            def competing_link(_temporary, target, **_kwargs):
                Path(target).write_text("created by another process")
                raise FileExistsError(target)

            with patch.object(fileops.os, "link", side_effect=competing_link):
                with self.assertRaises(FileExistsError):
                    fileops.copy_item(source, destination)
            self.assertEqual(destination.read_text(), "created by another process")
            self.assertEqual(source.read_text(), "source")
            self.assertFalse(list(root.glob(".*.copy-tmp")))

    def test_format_size(self):
        self.assertEqual(fileops.format_size(42), "42 B")
        self.assertEqual(fileops.format_size(1024), "1.0 KB")


if __name__ == "__main__":
    unittest.main()
