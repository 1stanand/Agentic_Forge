import argparse
import getpass
import logging
import sys

from forge.api.auth import hash_password
from forge.core.db import get_conn, get_cursor, release_conn

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def create_user(username: str, display_name: str, password: str = None, is_admin: bool = False):
    if not password:
        password = getpass.getpass(f"Enter password for {username}: ")
        confirm = getpass.getpass("Confirm password: ")
        if password != confirm:
            logger.error("Passwords do not match")
            return False

    try:
        conn = get_conn()
        with get_cursor(conn) as cursor:
            password_hash = hash_password(password)
            cursor.execute(
                """
                INSERT INTO users (username, display_name, password_hash, is_admin, is_active)
                VALUES (%s, %s, %s, %s, TRUE)
                """,
                (username, display_name, password_hash, is_admin)
            )
        logger.info(f"User '{username}' created successfully {'(admin)' if is_admin else ''}")
        release_conn(conn)
        return True
    except Exception as e:
        logger.error(f"Failed to create user: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Create a Forge user')
    parser.add_argument('--username', required=True, help='Username')
    parser.add_argument('--display', required=True, help='Display name')
    parser.add_argument('--password', help='Password (will prompt if not provided)')
    parser.add_argument('--admin', action='store_true', help='Make user an admin')
    args = parser.parse_args()

    if create_user(args.username, args.display, args.password, args.admin):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
