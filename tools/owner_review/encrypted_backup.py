"""Portable encrypted owner-review snapshots. No credentials are stored here.

V1 envelope: magic (6 bytes), scrypt salt (16), AES-GCM nonce (12), then
ciphertext and 16-byte authentication tag. The header is authenticated as AAD.
Scrypt parameters are fixed at N=32768, r=8, p=1, output 32 bytes.
This is a ForestProof-specific format, not an interoperable standard format.
"""
import argparse
from contextlib import closing
import getpass
import os
from pathlib import Path
import secrets
import sqlite3
import sys
import tempfile
import warnings

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

from tools.owner_review import store

MAGIC = b'FPOR1\x00'
SALT_SIZE = 16
NONCE_SIZE = 12
HEADER_SIZE = len(MAGIC) + SALT_SIZE + NONCE_SIZE
MAX_DATABASE = 32 * 1024 * 1024
MAX_ENVELOPE = MAX_DATABASE + HEADER_SIZE + 16


class BackupError(Exception):
    """A sanitized failure to create or verify an encrypted backup."""


def _key(passphrase: str, salt: bytes) -> bytes:
    if not isinstance(passphrase, str) or not 24 <= len(passphrase) <= 512:
        raise BackupError('Recovery passphrase must contain 24 to 512 characters.')
    return Scrypt(salt=salt, length=32, n=2**15, r=8, p=1).derive(passphrase.encode('utf-8'))


def _check(db: sqlite3.Connection) -> dict:
    db.row_factory = sqlite3.Row
    if [row[0] for row in db.execute('PRAGMA integrity_check')] != ['ok']:
        raise BackupError('Snapshot integrity check failed.')
    return store.summarize(db)


def _bounded(db: sqlite3.Connection) -> None:
    pages = db.execute('PRAGMA page_count').fetchone()[0]
    size = db.execute('PRAGMA page_size').fetchone()[0]
    if pages <= 0 or size <= 0 or pages * size > MAX_DATABASE:
        raise BackupError('Snapshot is outside the supported size limit.')


def snapshot_bytes(source: Path) -> bytes:
    """Read a consistent verified SQLite snapshot directly into memory."""
    source = Path(source).resolve(strict=True)
    if not source.is_file():
        raise BackupError('Snapshot source is not a regular file.')
    with closing(sqlite3.connect(source.as_uri() + '?mode=ro', uri=True)) as reader:
        reader.execute('PRAGMA query_only = ON')
        _bounded(reader)
        with closing(sqlite3.connect(':memory:')) as memory:
            reader.backup(memory)
            _bounded(memory)
            _check(memory)
            data = memory.serialize()
    if not 0 < len(data) <= MAX_DATABASE:
        raise BackupError('Snapshot is outside the supported size limit.')
    return data


def encrypt_snapshot(source: Path, passphrase: str) -> bytes:
    data = snapshot_bytes(source)
    header = MAGIC + secrets.token_bytes(SALT_SIZE) + secrets.token_bytes(NONCE_SIZE)
    key = _key(passphrase, header[len(MAGIC):len(MAGIC) + SALT_SIZE])
    return header + AESGCM(key).encrypt(header[-NONCE_SIZE:], data, header)


def decrypt_snapshot(envelope: bytes, passphrase: str) -> sqlite3.Connection:
    """Authenticate and validate in memory; caller must close the returned DB."""
    if not isinstance(envelope, bytes) or not HEADER_SIZE + 16 < len(envelope) <= MAX_ENVELOPE:
        raise BackupError('Encrypted backup size is invalid.')
    header = envelope[:HEADER_SIZE]
    if not header.startswith(MAGIC):
        raise BackupError('Encrypted backup format is not recognized.')
    key = _key(passphrase, header[len(MAGIC):len(MAGIC) + SALT_SIZE])
    try:
        data = AESGCM(key).decrypt(header[-NONCE_SIZE:], envelope[HEADER_SIZE:], header)
    except InvalidTag as error:
        raise BackupError('Recovery passphrase is wrong or backup is damaged.') from error
    if not 0 < len(data) <= MAX_DATABASE:
        raise BackupError('Decrypted snapshot size is invalid.')
    memory = sqlite3.connect(':memory:')
    try:
        memory.deserialize(data)
        _bounded(memory)
        _check(memory)
        return memory
    except BaseException:
        memory.close()
        raise


def _write_new(destination: Path, data: bytes) -> None:
    """Publish bytes atomically without replacing an existing path.

    The parent directory must be trusted, private and on a filesystem supporting
    hard links. POSIX mode 0600 is requested; on Windows, directory ACLs apply.
    """
    destination = Path(destination).absolute()
    if not destination.parent.is_dir():
        raise BackupError('Destination directory does not exist.')
    fd, name = tempfile.mkstemp(prefix='.fp-recovery-', dir=destination.parent)
    temporary = Path(name)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, destination)  # fails closed if destination already exists
    finally:
        temporary.unlink(missing_ok=True)
    if os.name == 'posix':
        # Ensure the hard-link publication is durable where directory fsync is supported.
        directory_fd = os.open(destination.parent, os.O_RDONLY | getattr(os, 'O_DIRECTORY', 0))
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)


def write_new_envelope(destination: Path, envelope: bytes) -> None:
    if not isinstance(envelope, bytes) or not HEADER_SIZE + 16 < len(envelope) <= MAX_ENVELOPE:
        raise BackupError('Invalid encrypted backup size.')
    _write_new(destination, envelope)


def read_envelope(source: Path) -> bytes:
    with Path(source).open('rb') as stream:
        data = stream.read(MAX_ENVELOPE + 1)
    if len(data) > MAX_ENVELOPE:
        raise BackupError('Encrypted backup size is invalid.')
    return data


def write_restored_database(destination: Path, memory: sqlite3.Connection) -> None:
    """Write a validated database only into an explicitly trusted directory.

    This writes plaintext, so users must provision a private destination. On
    Windows the containing directory's ACL controls access. Existing databases
    and SQLite sidecars are never overwritten.
    """
    destination = Path(destination).absolute()
    for suffix in ('-wal', '-shm', '-journal'):
        if os.path.lexists(str(destination) + suffix):
            raise BackupError('A destination SQLite sidecar already exists.')
    _bounded(memory)
    _check(memory)
    _write_new(destination, memory.serialize())


def main() -> int:
    parser = argparse.ArgumentParser(description='Create or restore an encrypted private owner review backup.')
    commands = parser.add_subparsers(dest='command', required=True)
    for name in ('backup', 'restore', 'verify'):
        command = commands.add_parser(name)
        command.add_argument('source', type=Path)
        if name != 'verify':
            command.add_argument('destination', type=Path)
    args = parser.parse_args()
    if not sys.stdin.isatty():
        print('A private interactive terminal is required.', file=sys.stderr)
        return 1
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('error', getpass.GetPassWarning)
            phrase = getpass.getpass('Recovery passphrase (hidden): ')
            if args.command == 'backup' and phrase != getpass.getpass('Confirm recovery passphrase (hidden): '):
                raise BackupError('Passphrases did not match.')
        if args.command == 'backup':
            write_new_envelope(args.destination, encrypt_snapshot(args.source, phrase))
            print('Encrypted backup created. No remote transfer was performed.')
        else:
            with closing(decrypt_snapshot(read_envelope(args.source), phrase)) as db:
                if args.command == 'restore':
                    write_restored_database(args.destination, db)
                    print('Recovery verified and restored to the private destination.')
                else:
                    print('Recovery passphrase and database integrity verified in memory.')
        return 0
    except (BackupError, store.ReviewError, OSError, sqlite3.Error, ValueError, UnicodeError, getpass.GetPassWarning):
        print('Backup or restore did not complete; check the private inputs and destination.', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
