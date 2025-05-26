import os
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.tools.sql_database.tool import (
    InfoSQLDatabaseTool,
    ListSQLDatabaseTool,
    QuerySQLDataBaseTool,
)
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from .tool_error_callback import tool_error_builder


def get_postgre_sql_toolkit(db_name="pg"):
    # Put env here so testing can be done without dotenv kicking out monkeypatch
    postgre_host = os.getenv("POSTGRE_DS_HOST")
    postgre_port = os.getenv("POSTGRE_DS_PORT")
    postgre_username = os.getenv("POSTGRE_DS_USERNAME")
    postgre_password = os.getenv("POSTGRE_DS_PASSWORD")
    postgre_db = os.getenv("POSTGRE_DS_DB")

    postgre_conn = f'postgresql://{postgre_username}:{postgre_password}@{postgre_host}:{postgre_port}/{postgre_db}'
    try:
        print(postgre_conn)
        postgre_engine = create_engine(
            postgre_conn,
            connect_args={"connect_timeout": 1},  # PostgreSQL-specific timeout setting
            pool_pre_ping=True  # Ensures the connection is alive before using it
        )

        postgre_db = SQLDatabase(postgre_engine, include_tables=[])
        return [
            InfoSQLDatabaseTool(db=postgre_db, name=f"{db_name}_sql_db_info"),
            ListSQLDatabaseTool(db=postgre_db, name=f"{db_name}_sql_db_list_tables"),
            QuerySQLDataBaseTool(db=postgre_db, name=f"{db_name}_sql_db_query")
        ]

    except OperationalError as e:
        error_msg = f"Failed to connect to PostgreSQL (timeout or othepostgre_sql_db_r issue): {e}"
        return [tool_error_builder(error_msg, name="pg_sql_db_error")]
