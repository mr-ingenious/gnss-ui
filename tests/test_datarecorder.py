# project/test.py

import unittest
import pathlib as pl
import os


from src.data_recorder import DataRecorder, DataRecorderStatus


class TestDatarecorderBase(unittest.TestCase):
    def __init__(self):
        pass
    
    def assertIsFile(self, path):
        if not pl.Path(path).resolve().is_file():
            raise AssertionError("File does not exist: %s" % str(path))


class TestDatarecorder(TestDatarecorderBase):

    def __init__(self):
        super().__init__()
        self.db_filename = "test.db"

    def test_status_after_init(self):
        datarecorder = DataRecorder(db_file=self.db_filename)
        self.assertEqual(
            datarecorder.get_status(),
            DataRecorderStatus.RECORDING_IDLE,
            "wrong recorder status after init.",
        )

    def test_recording_none_after_init(self):
        datarecorder = DataRecorder(db_file=self.db_filename)
        self.assertEqual(
            datarecorder.get_current_recording(),
            None,
            "current recording is not none after init",
        )

    def test_database_file_exists_after_init(self):
        datarecorder = DataRecorder(db_file=self.db_filename)

        path = pl.Path(self.db_filename)

        self.assertIsFile(path)

    def tearDown(self):
        try:
            os.remove(self.db_filename)
        except OSError:
            pass

        super().tearDown()


if __name__ == "__main__":
    unittest.main()
