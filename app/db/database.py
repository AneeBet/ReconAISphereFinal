import struct

from urllib.parse import quote_plus

from azure.identity import ManagedIdentityCredential

from sqlalchemy import create_engine
from sqlalchemy import event

from app.core.config import settings
from app.db.base import Base

import app.models


SQL_COPT_SS_ACCESS_TOKEN = 1256


def get_access_token():

    credential = ManagedIdentityCredential()

    token = credential.get_token(
        "https://database.windows.net/.default"
    )

    token_bytes = token.token.encode(
        "utf-16-le"
    )

    return struct.pack(

        f"<I{len(token_bytes)}s",

        len(token_bytes),

        token_bytes

    )


odbc_connection_string = (
    "Driver={ODBC Driver 18 for SQL Server};"
    f"Server=tcp:{settings.AZURE_SQL_SERVER},1433;"
    f"Database={settings.AZURE_SQL_DATABASE};"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
    "Connection Timeout=30;"
)


engine = create_engine(

    "mssql+pyodbc:///?odbc_connect="
    + quote_plus(odbc_connection_string),

    pool_pre_ping=True

)


@event.listens_for(
    engine,
    "do_connect"
)
def provide_token(
    dialect,
    conn_rec,
    cargs,
    cparams
):
    cparams["attrs_before"] = {
        SQL_COPT_SS_ACCESS_TOKEN: get_access_token()
    }


def create_database():

    Base.metadata.create_all(
        bind=engine
    )
