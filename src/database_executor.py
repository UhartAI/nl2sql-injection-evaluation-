"""
Database executor module for SQL injection testing.
"""

import sqlite3
import mysql.connector
import psycopg2
import pymssql
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple
from contextlib import contextmanager
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseExecutor(ABC):
    """Abstract base class for database executors."""

    @abstractmethod
    def execute(self, query: str) -> Tuple[bool, Dict[str, Any]]:
        """Execute a query and return (success, result_data)."""
        pass

    @abstractmethod
    def get_db_type(self) -> str:
        """Return the database type."""
        pass


class SQLiteExecutor(DatabaseExecutor):
    """Executor for SQLite databases."""

    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self.connection = None
        self._connect()

    def _connect(self):
        """Create a connection to SQLite database."""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row

    @contextmanager
    def _get_cursor(self):
        """Get a cursor with transaction management."""
        cursor = self.connection.cursor()
        try:
            yield cursor
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def execute(self, query: str) -> Tuple[bool, Dict[str, Any]]:
        """Execute a query in SQLite."""
        result = {
            "success": False,
            "data": [],
            "error": None,
            "execution_time_ms": 0,
            "rows_affected": 0,
        }

        start_time = time.time()

        try:
            with self._get_cursor() as cursor:
                cursor.execute(query)

                if query.strip().upper().startswith("SELECT"):
                    rows = cursor.fetchall()
                    result["data"] = [dict(row) for row in rows]
                    result["rows_affected"] = len(rows)
                else:
                    result["rows_affected"] = cursor.rowcount

                result["success"] = True

        except sqlite3.Error as e:
            result["error"] = str(e)
            logger.warning(f"SQLite execution error: {e}")

        except Exception as e:
            result["error"] = str(e)
            logger.error(f"SQLite unexpected error: {e}")

        finally:
            result["execution_time_ms"] = (time.time() - start_time) * 1000

        return result["success"], result

    def get_db_type(self) -> str:
        return "sqlite"


class MySQLExecutor(DatabaseExecutor):
    """Executor for MySQL databases."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 3306,
        user: str = "nl2sql_user",
        password: str = "nl2sql_password",
        database: str = "nl2sql_db",
    ):
        self.config = {
            "host": host,
            "port": port,
            "user": user,
            "password": password,
            "database": database,
        }
        self.connection = None
        self._connect()

    def _connect(self):
        """Create a connection to MySQL database."""
        self.connection = mysql.connector.connect(**self.config)

    @contextmanager
    def _get_cursor(self):
        """Get a cursor with transaction management."""
        cursor = self.connection.cursor(dictionary=True)
        try:
            yield cursor
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def execute(self, query: str) -> Tuple[bool, Dict[str, Any]]:
        """Execute a query in MySQL."""
        result = {
            "success": False,
            "data": [],
            "error": None,
            "execution_time_ms": 0,
            "rows_affected": 0,
        }

        start_time = time.time()

        try:
            with self._get_cursor() as cursor:
                cursor.execute(query)

                if query.strip().upper().startswith("SELECT"):
                    rows = cursor.fetchall()
                    result["data"] = rows
                    result["rows_affected"] = len(rows)
                else:
                    result["rows_affected"] = cursor.rowcount

                result["success"] = True

        except mysql.connector.Error as e:
            result["error"] = str(e)
            logger.warning(f"MySQL execution error: {e}")

        except Exception as e:
            result["error"] = str(e)
            logger.error(f"MySQL unexpected error: {e}")

        finally:
            result["execution_time_ms"] = (time.time() - start_time) * 1000

        return result["success"], result

    def get_db_type(self) -> str:
        return "mysql"


class PostgreSQLExecutor(DatabaseExecutor):
    """Executor for PostgreSQL databases."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 5432,
        user: str = "nl2sql_user",
        password: str = "nl2sql_password",
        database: str = "nl2sql_db",
    ):
        self.config = {
            "host": host,
            "port": port,
            "user": user,
            "password": password,
            "database": database,
        }
        self.connection = None
        self._connect()

    def _connect(self):
        """Create a connection to PostgreSQL database."""
        self.connection = psycopg2.connect(**self.config)

    @contextmanager
    def _get_cursor(self):
        """Get a cursor with transaction management."""
        cursor = self.connection.cursor()
        try:
            yield cursor
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def execute(self, query: str) -> Tuple[bool, Dict[str, Any]]:
        """Execute a query in PostgreSQL."""
        result = {
            "success": False,
            "data": [],
            "error": None,
            "execution_time_ms": 0,
            "rows_affected": 0,
        }

        start_time = time.time()

        try:
            with self._get_cursor() as cursor:
                cursor.execute(query)

                if query.strip().upper().startswith("SELECT"):
                    rows = cursor.fetchall()
                    result["data"] = [dict(zip([desc[0] for desc in cursor.description], row)) for row in rows]
                    result["rows_affected"] = len(rows)
                else:
                    result["rows_affected"] = cursor.rowcount

                result["success"] = True

        except psycopg2.Error as e:
            result["error"] = str(e)
            logger.warning(f"PostgreSQL execution error: {e}")

        except Exception as e:
            result["error"] = str(e)
            logger.error(f"PostgreSQL unexpected error: {e}")

        finally:
            result["execution_time_ms"] = (time.time() - start_time) * 1000

        return result["success"], result

    def get_db_type(self) -> str:
        return "postgresql"


class MSSQLExecutor(DatabaseExecutor):
    """Executor for Microsoft SQL Server databases."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 1433,
        user: str = "nl2sql_user",
        password: str = "nl2sql_password",
        database: str = "nl2sql_db",
    ):
        self.config = {
            "server": host,
            "port": port,
            "user": user,
            "password": password,
            "database": database,
        }
        self.connection = None
        self._connect()

    def _connect(self):
        """Create a connection to MSSQL database."""
        self.connection = pymssql.connect(**self.config)

    @contextmanager
    def _get_cursor(self):
        """Get a cursor with transaction management."""
        cursor = self.connection.cursor()
        try:
            yield cursor
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def execute(self, query: str) -> Tuple[bool, Dict[str, Any]]:
        """Execute a query in MSSQL."""
        result = {
            "success": False,
            "data": [],
            "error": None,
            "execution_time_ms": 0,
            "rows_affected": 0,
        }

        start_time = time.time()

        try:
            with self._get_cursor() as cursor:
                cursor.execute(query)

                if query.strip().upper().startswith("SELECT"):
                    rows = cursor.fetchall()
                    result["data"] = [dict(zip([desc[0] for desc in cursor.description], row)) for row in rows]
                    result["rows_affected"] = len(rows)
                else:
                    result["rows_affected"] = cursor.rowcount

                result["success"] = True

        except pymssql.Error as e:
            result["error"] = str(e)
            logger.warning(f"MSSQL execution error: {e}")

        except Exception as e:
            result["error"] = str(e)
            logger.error(f"MSSQL unexpected error: {e}")

        finally:
            result["execution_time_ms"] = (time.time() - start_time) * 1000

        return result["success"], result

    def get_db_type(self) -> str:
        return "mssql"


class DatabaseExecutorFactory:
    """Factory class for creating database executors."""

    @staticmethod
    def create_executor(db_type: str, **kwargs) -> DatabaseExecutor:
        """
        Create a database executor based on type.

        Args:
            db_type: "sqlite", "mysql", "postgresql", or "mssql"
            **kwargs: Additional arguments for specific database

        Returns:
            DatabaseExecutor instance
        """
        if db_type == "sqlite":
            return SQLiteExecutor(**kwargs)
        elif db_type == "mysql":
            return MySQLExecutor(**kwargs)
        elif db_type == "postgresql":
            return PostgreSQLExecutor(**kwargs)
        elif db_type == "mssql":
            return MSSQLExecutor(**kwargs)
        else:
            raise ValueError(f"Unsupported database type: {db_type}")