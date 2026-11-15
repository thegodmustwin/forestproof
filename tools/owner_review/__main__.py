"""Initialize, open, or back up the private historical owner review."""

import argparse
import getpass
from pathlib import Path
import sqlite3
import warnings

from services.api.app.sqlite_copy import RecoveryError
from tools.owner_review import store, web


def configure_password(database: Path):
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", getpass.GetPassWarning)
            password = getpass.getpass("Choose a private owner password (12 or more characters): ")
            confirmation = getpass.getpass("Confirm the password: ")
    except (EOFError, getpass.GetPassWarning) as error:
        raise store.ReviewError("Open the setup in an interactive terminal to enter the password privately.") from error
    if password != confirmation:
        raise store.ReviewError("The passwords did not match. Run the setup again.")
    store.set_password(database, password)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", required=True, type=Path)
    commands = parser.add_subparsers(dest="command", required=True)
    initialize = commands.add_parser("init")
    initialize.add_argument("--archive", required=True, type=Path)
    initialize.add_argument("--owner-name", required=True)
    start = commands.add_parser("start")
    start.add_argument("--port", type=int, default=web.PORT)
    start.add_argument("--open-browser", action="store_true")
    copy = commands.add_parser("backup")
    copy.add_argument("destination", type=Path)
    args = parser.parse_args()

    try:
        if args.command == "init":
            store.initialize(args.database, args.archive, args.owner_name)
            print("Historical source receipt verified. Owner review pending.")
        elif args.command == "backup":
            store.copy_review(args.database, args.destination)
            print("Review backup was copied and verified.")
        else:
            if not 1024 <= args.port <= 65535:
                parser.error("Choose an unprivileged port.")
            if not store.has_password(args.database):
                configure_password(args.database)
                print("Use owner as the username in the local browser.")
            web.run(args.database, args.port, open_browser=args.open_browser)
    except store.ReviewError as error:
        parser.exit(1, f"{error}\n")
    except (OSError, RecoveryError, sqlite3.Error):
        parser.exit(1, "Check the private archive and database paths, or the local listener port.\n")


if __name__ == "__main__":
    main()
