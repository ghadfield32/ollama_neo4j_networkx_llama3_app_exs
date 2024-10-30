# database_setup.py
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, ForeignKey
import os

# Define the fixed path for example databases
DB_PATH = '/workspaces/custom_ollama_docker/data/graph_chroma_dbs/networkx'

# Ensure the directory exists
os.makedirs(DB_PATH, exist_ok=True)

def setup_databases(debug=False):
    engine1 = create_engine(f'sqlite:///{os.path.join(DB_PATH, "example1.db")}')
    engine2 = create_engine(f'sqlite:///{os.path.join(DB_PATH, "example2.db")}')
    metadata1 = MetaData()
    metadata2 = MetaData()

    # Define tables for the first database
    Table('employees', metadata1, Column('id', Integer, primary_key=True), Column('name', String),
          Column('department', String), Column('salary', Integer), Column('manager_id', Integer, ForeignKey('managers.id')))
    Table('managers', metadata1, Column('id', Integer, primary_key=True), Column('name', String),
          Column('department', String))
    Table('departments', metadata1, Column('id', Integer, primary_key=True), Column('name', String),
          Column('location', String))

    # Define tables for the second database
    Table('staff', metadata2, Column('id', Integer, primary_key=True), Column('full_name', String),
          Column('dept', String), Column('wage', Integer), Column('supervisor_id', Integer, ForeignKey('supervisors.id')))
    Table('supervisors', metadata2, Column('id', Integer, primary_key=True), Column('full_name', String),
          Column('dept', String))
    Table('office_locations', metadata2, Column('id', Integer, primary_key=True), Column('office_name', String),
          Column('address', String))

    # Create tables in the databases
    metadata1.create_all(engine1)
    metadata2.create_all(engine2)
    
    if debug:
        print("Database setup completed for example1 and example2 with tables for employees, managers, and departments.")

    return engine1, engine2, metadata1, metadata2

def main(debug=False):
    setup_databases(debug=debug)

if __name__ == "__main__":
    main(debug=True)

