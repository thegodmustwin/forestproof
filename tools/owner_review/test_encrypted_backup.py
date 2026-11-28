from contextlib import closing
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sqlite3
import getpass
import warnings
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from tools.owner_review import encrypted_backup as backup, store
from tools.owner_review.test_review import fixture


PASSPHRASE = 'fixture-only-long-random-looking-value-321'


class TestEncryptedBackup(TestCase):
    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.directory = Path(temp.name)
        archive = self.directory / 'archive'
        fixture(archive)
        self.database = self.directory / 'review.sqlite3'
        store.initialize(self.database, archive, 'Fixture owner')
        store.set_password(self.database, 'test-only-password')
        store.record_review(self.database, 'a' * 32, 'keep_open',
                            (datetime.now(timezone.utc).date() + timedelta(days=10)).isoformat(),
                            'Synthetic review.', now=datetime.now(timezone.utc))

    def test_encrypt_restore_receipt_dossier_and_review(self):
        envelope = backup.encrypt_snapshot(self.database, PASSPHRASE)
        self.assertNotIn(b'Synthetic review.', envelope)
        self.assertNotIn(b'SQLite format 3', envelope)
        out = self.directory / 'case.enc'
        backup.write_new_envelope(out, envelope)
        with closing(backup.decrypt_snapshot(out.read_bytes(), PASSPHRASE)) as db:
            self.assertEqual(store.summarize(db), store.snapshot(self.database))
            self.assertEqual(store.stored_documents(db)['observation.json'], store.original_receipt(self.database))

    def test_wrong_password_tampering_and_truncation_fail(self):
        envelope = backup.encrypt_snapshot(self.database, PASSPHRASE)
        with self.assertRaises(backup.BackupError):
            backup.decrypt_snapshot(envelope, 'incorrect-password-value-long-enough')
        for index in (len(backup.MAGIC), backup.HEADER_SIZE, len(envelope) - 1):
            changed = bytearray(envelope)
            changed[index] ^= 1
            with self.assertRaises(backup.BackupError):
                backup.decrypt_snapshot(bytes(changed), PASSPHRASE)
        with self.assertRaises(backup.BackupError):
            backup.decrypt_snapshot(envelope[:backup.HEADER_SIZE], PASSPHRASE)

    def test_existing_destination_is_never_replaced(self):
        envelope = backup.encrypt_snapshot(self.database, PASSPHRASE)
        out = self.directory / 'existing.enc'
        out.write_bytes(b'existing')
        with self.assertRaises(FileExistsError):
            backup.write_new_envelope(out, envelope)
        self.assertEqual(out.read_bytes(), b'existing')
        self.assertEqual(list(self.directory.glob('.fp-recovery-*')), [])

    def test_rejects_wrong_source_and_invalid_passphrase(self):
        other = self.directory / 'other.sqlite3'
        with closing(sqlite3.connect(other)) as db, db:
            db.execute('CREATE TABLE demo (id INTEGER)')
        with self.assertRaises(store.ReviewError):
            backup.encrypt_snapshot(other, PASSPHRASE)
        with self.assertRaises(backup.BackupError):
            backup.encrypt_snapshot(self.database, 'short')

    def test_restore_requires_fresh_destination(self):
        envelope = backup.encrypt_snapshot(self.database, PASSPHRASE)
        restored = self.directory / 'restored.sqlite3'
        with closing(backup.decrypt_snapshot(envelope, PASSPHRASE)) as db:
            backup.write_restored_database(restored, db)
            self.assertEqual(store.snapshot(restored), store.snapshot(self.database))
            with self.assertRaises(FileExistsError):
                backup.write_restored_database(restored, db)
        restored.unlink()
        sidecar = Path(str(restored) + '-wal')
        sidecar.write_bytes(b'fixture')
        with closing(backup.decrypt_snapshot(envelope, PASSPHRASE)) as db:
            with self.assertRaises(backup.BackupError):
                backup.write_restored_database(restored, db)

    def test_cli_backup_verify_and_restore(self):
        encrypted = self.directory / 'cli.enc'
        restored = self.directory / 'cli.sqlite3'
        with patch('sys.stdin.isatty', return_value=True), patch('getpass.getpass', return_value=PASSPHRASE):
            with patch('sys.argv', ['backup', 'backup', str(self.database), str(encrypted)]):
                self.assertEqual(backup.main(), 0)
            with patch('sys.argv', ['backup', 'verify', str(encrypted)]):
                self.assertEqual(backup.main(), 0)
            with patch('sys.argv', ['backup', 'restore', str(encrypted), str(restored)]):
                self.assertEqual(backup.main(), 0)
        self.assertEqual(store.snapshot(restored), store.snapshot(self.database))

    def test_cli_refuses_prompt_when_input_could_echo(self):
        destination = self.directory / 'not-created.enc'
        def insecure_prompt(*_args, **_kwargs):
            warnings.warn('could echo', getpass.GetPassWarning)
        with patch('sys.stdin.isatty', return_value=True), patch('getpass.getpass', side_effect=insecure_prompt):
            with patch('sys.argv', ['backup', 'backup', str(self.database), str(destination)]):
                self.assertEqual(backup.main(), 1)
        self.assertFalse(destination.exists())
