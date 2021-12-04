import pandas as pd
import sqlalchemy

# Thanks dafrenchy for this plug-and-play mariadb connection.
db_user = "root"
db_pass = "secret"  # pragma: allowlist secret
db_host = "localhost:3306"
db_database = "mysql"
connect_string = (
    f"mariadb+mariadbconnector://{db_user}:{db_pass}@{db_host}/{db_database}"
)
# pragma: allowlist secret

sql_engine = sqlalchemy.create_engine(connect_string)

query = """
    SELECT * FROM DB
"""
df = pd.read_sql_query(query, sql_engine)
