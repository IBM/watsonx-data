from contextlib import contextmanager

from prestodb.dbapi import Cursor, Connection
from dbt.adapters.contracts.connection import AdapterResponse, Credentials
from dbt.adapters.sql import SQLConnectionManager
from dbt.logger import GLOBAL_LOGGER as logger
from dbt.adapters.exceptions.connection import FailedToConnectError
from dataclasses import dataclass
from typing import Optional, Dict, Union
from dbt_common.helper_types import Port
from dbt_common.exceptions import DbtDatabaseError, DbtRuntimeError

from datetime import date, datetime
import decimal
import re
import prestodb
from prestodb.transaction import IsolationLevel
import sqlparse

class CustomConnection(Connection):    
    def cursor(self):
        if self.isolation_level != IsolationLevel.AUTOCOMMIT:
            if self.transaction is None:
                self.start_custom_transaction()
        if self.transaction is not None:
            request = self.transaction._request
        else:
            request = self._create_request()
        return CustomCursor(self, request)

class CustomCursor(Cursor):
    def query_id(self) -> Optional[str]:
        return self._query.query_id

    def query(self) -> Optional[str]:
        return self._query._sql
   
    def __getattr__(self, attr):
        return getattr(self._cursor, attr)

class PrestoAdapterResponse(AdapterResponse):
    query: str = ""
    query_id: str = ""

    def __init__(self, _message: str, query: str, query_id: str, rows_affected: int):
        super().__init__(_message=_message)
        self.query = query
        self.query_id = query_id
        self.rows_affected = rows_affected


@dataclass
class PrestoCredentials(Credentials):
    host: str
    port: Port
    user: str
    password: Optional[str] = None
    method: Optional[str] = None
    http_headers: Optional[Dict[str, str]] = None
    http_scheme: Optional[str] = None
    ssl_verify: Optional[Union[bool, str]] = True
    _ALIASES = {
        'catalog': 'database'
    }

    @property
    def type(self):
        return 'presto'

    @property
    def unique_field(self):
        return self.host

    def _connection_keys(self):
        return ('host', 'port', 'user', 'database', 'schema', 'ssl_verify')


class ConnectionWrapper(object):
    """Wrap a Presto connection in a way that accomplishes two tasks:

        - prefetch results from execute() calls so that presto calls actually
            persist to the db but then present the usual cursor interface
        - provide `cancel()` on the same object as `commit()`/`rollback()`/...

    """

    def __init__(self, handle):
        self.handle = handle
        self._cursor = None
        self._fetch_result = None

    def cursor(self):
        self._cursor = self.handle.cursor()
        return self

    def cancel(self):
        if self._cursor is not None:
            self._cursor.cancel()

    def close(self):
        # this is a noop on presto, but pass it through anyway
        self.handle.close()

    def commit(self):
        pass

    def rollback(self):
        pass

    def start_transaction(self):
        pass

    def fetchall(self):
        if self._cursor is None:
            return None

        if self._fetch_result is not None:
            ret = self._fetch_result
            self._fetch_result = None
            return ret

        return None

    def execute(self, sql, bindings=None):

        if bindings is not None:
            # presto doesn't actually pass bindings along so we have to do the
            # escaping and formatting ourselves
            bindings = tuple(self._escape_value(b) for b in bindings)
            sql = sql % bindings

            result = self._cursor.execute(sql)
        else:
            result = self._cursor.execute(sql, params=bindings)
        self._fetch_result = self._cursor.fetchall()
        return result

    @property
    def description(self):
        return self._cursor.description

    @classmethod
    def _escape_value(cls, value):
        """A not very comprehensive system for escaping bindings.

        I think "'" (a single quote) is the only character that matters.
        """
        numbers = (decimal.Decimal, int, float)
        if value is None:
            return 'NULL'
        elif isinstance(value, str):
            return "'{}'".format(value.replace("'", "''"))
        elif isinstance(value, numbers):
            return value
        elif isinstance(value, datetime):
            time_formatted = value.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            return "TIMESTAMP '{}'".format(time_formatted)
        elif isinstance(value, date):
            date_formatted = value.strftime("%Y-%m-%d")
            return "DATE '{}'".format(date_formatted)
        else:
            raise ValueError('Cannot escape {}'.format(type(value)))


class PrestoConnectionManager(SQLConnectionManager):
    TYPE = 'presto'

    @contextmanager
    def exception_handler(self, sql):
        try:
            yield
        # TODO: introspect into `DatabaseError`s and expose `errorName`,
        # `errorType`, etc instead of stack traces full of garbage!
        except prestodb.exceptions.Error as e:
            res = str(e)
            if "Failed to establish a new connection" in res:
                raise FailedToConnectError(res) from e
            if isinstance(e, prestodb.exceptions.PrestoQueryError):
                logger.debug("Presto query id: {}".format(e.query_id))
            logger.debug("Presto error: {}".format(res))

            raise DbtDatabaseError(res)
        except Exception as exc:
            logger.debug("Error while running:\n{}".format(sql))
            logger.debug(exc)
            raise DbtRuntimeError(str(exc))

    def add_begin_query(self):
        pass

    def add_commit_query(self):
        pass

    @classmethod
    def open(cls, connection):
        if connection.state == 'open':
            logger.debug('Connection is already open, skipping open.')
            return connection

        credentials = connection.credentials
        if credentials.method == 'BasicAuth':
            auth = prestodb.auth.BasicAuthentication(
                credentials.user,
                credentials.password,
            )
            if credentials.http_scheme and credentials.http_scheme != "https":
                raise DbtRuntimeError(
                    "http_scheme must be set to 'https' for 'BasicAuth' method."
                )
            http_scheme = "https"
        else:
            auth = prestodb.constants.DEFAULT_AUTH
            http_scheme = credentials.http_scheme or "http"

        # it's impossible for presto to fail here as 'connections' are actually
        # just cursor factories.
        presto_conn = CustomConnection(
            host=credentials.host,
            port=credentials.port,
            user=credentials.user,
            catalog=credentials.database,
            schema=credentials.schema,
            http_scheme=http_scheme,
            http_headers=credentials.http_headers,
            auth=auth,
            isolation_level=IsolationLevel.AUTOCOMMIT
        )
        presto_conn._http_session.verify = credentials.ssl_verify
        connection.state = 'open'
        connection.handle = ConnectionWrapper(presto_conn)
        return connection

    @classmethod
    def get_response(cls, cursor):
        # this is lame, but the cursor doesn't give us anything useful.
        return PrestoAdapterResponse(
            _message = "SUCCESS",
            query = cursor._cursor.query(),
            query_id = cursor._cursor.query_id(),
            rows_affected = cursor._cursor.rowcount
        )


    def cancel(self, connection):
        connection.handle.cancel()

    def add_query(self, sql, auto_begin=True,
                  bindings=None, abridge_sql_log=False):

        connection = None
        cursor = None

        # TODO: is this sufficient? Largely copy+pasted from snowflake, so
        # there's some common behavior here we can maybe factor out into the
        # SQLAdapter?
        queries = [q.rstrip(';') for q in sqlparse.split(sql)]

        for individual_query in queries:
            # hack -- after the last ';', remove comments and don't run
            # empty queries. this avoids using exceptions as flow control,
            # and also allows us to return the status of the last cursor
            without_comments = re.sub(
                re.compile('^.*(--.*)$', re.MULTILINE),
                '', individual_query).strip()

            if without_comments == "":
                continue

            parent = super(PrestoConnectionManager, self)
            connection, cursor = parent.add_query(
                individual_query, auto_begin, bindings,
                abridge_sql_log
            )

        if cursor is None:
            raise DbtRuntimeError(
                "Tried to run an empty query on model '{}'. If you are "
                "conditionally running\nsql, eg. in a model hook, make "
                "sure your `else` clause contains valid sql!\n\n"
                "Provided SQL:\n{}".format(connection.name, sql)
            )

        return connection, cursor
    
    