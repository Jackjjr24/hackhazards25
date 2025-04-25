from langchain_community.utilities import SQLDatabase

def init_database(db_type: str, user: str, password: str, host: str, port: str, database: str):
    if db_type == "MySQL":
        db_uri = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"
    elif db_type == "PostgreSQL":
        db_uri = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
    else:
        raise ValueError("Unsupported database type")
    return SQLDatabase.from_uri(db_uri), db_uri

def run_query(db, query: str):
    return db.run(query)