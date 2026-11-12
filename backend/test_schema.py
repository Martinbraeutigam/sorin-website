"""SQLite schema regression tests. Run: python -m unittest discover -s backend -p 'test_*.py' -v"""
from pathlib import Path
import sqlite3
import unittest

SCHEMA = Path(__file__).with_name("schema.sql")


class LibrarySchemaTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.db.execute("PRAGMA foreign_keys = ON")
        self.db.executescript(SCHEMA.read_text(encoding="utf-8"))
        self.db.execute("INSERT INTO users VALUES (?,?,?,?,?,?,?)", ("u1", "Creator", "a@example.com", "salt", "hash", "member", 1))
        self.db.execute("INSERT INTO users VALUES (?,?,?,?,?,?,?)", ("u2", "Reviewer", "b@example.com", "salt", "hash", "admin", 1))
        self.db.execute("INSERT INTO resources (id,owner_id,kind,title,category,description,media_type,stored_name,file_hash,created_at) VALUES (?,?,?,?,?,?,?,?,?,?)", ("r1", "u1", "emoji", "Hello", "gaming", "original", "image/png", "file.png", "sha", 1))

    def tearDown(self):
        self.db.close()

    def test_integrity_and_tables(self):
        self.assertEqual(self.db.execute("PRAGMA integrity_check").fetchone()[0], "ok")
        tables = {r[0] for r in self.db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        self.assertTrue({"users", "sessions", "resources", "ratings", "points"} <= tables)

    def test_case_insensitive_identity(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("INSERT INTO users VALUES (?,?,?,?,?,?,?)", ("u3", "creator", "c@example.com", "salt", "hash", "member", 1))
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("INSERT INTO users VALUES (?,?,?,?,?,?,?)", ("u3", "other", "A@EXAMPLE.COM", "salt", "hash", "member", 1))

    def test_resource_constraints(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("UPDATE resources SET kind='bot' WHERE id='r1'")
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("UPDATE resources SET status='published' WHERE id='r1'")

    def test_foreign_keys(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("INSERT INTO sessions VALUES ('token','unknown',999)")

    def test_ratings(self):
        self.db.execute("INSERT INTO ratings VALUES ('u2','r1',5,1)")
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("INSERT INTO ratings VALUES ('u2','r1',4,2)")
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("INSERT INTO ratings VALUES ('u1','r1',6,2)")

    def test_points(self):
        self.db.execute("INSERT INTO points VALUES ('p1','u1','r1',20,1)")
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("INSERT INTO points VALUES ('p2','u1','r1',20,2)")
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("INSERT INTO points VALUES ('p3','u1','r1',-1,2)")

    def test_pending_and_idempotent_schema(self):
        self.assertEqual(self.db.execute("SELECT status FROM resources WHERE id='r1'").fetchone()[0], "pending")
        self.db.executescript(SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM resources").fetchone()[0], 1)


if __name__ == "__main__":
    unittest.main()
