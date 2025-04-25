import os
from sqlalchemy import create_engine, inspect
from graphviz import Digraph

def generate_er_diagram(db_uri, output_file="static/er_diagram"):
    engine = create_engine(db_uri)
    inspector = inspect(engine)
    dot = Digraph(format="png")

    for table in inspector.get_table_names():
        dot.node(table, table)
        for col in inspector.get_columns(table):
            dot.node(f"{table}_{col['name']}", col['name'], shape='ellipse')
            dot.edge(table, f"{table}_{col['name']}")

    filepath = dot.render(filename=output_file, cleanup=True)
    return filepath