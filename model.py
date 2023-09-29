# Model component of ArgMarkNet Web Crawler

import os
import sys
import pandas as pd
import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

# Generic function to read the source csv files and convert them to dictionaries
def read_csv_to_dict(file_name):
  try:
    df = pd.read_csv(file_name, header=None)
    data_dict = df.set_index(0)[1].to_dict()
    return data_dict
  except FileNotFoundError as e:
    print(f"File not found: {e}")
    sys.exit(1)
  except pd.errors.ParserError as e:
    print(f"Parsing error: {e}")
    sys.exit(1)

# Function to read the excel file and return it as a pandas dataframe
def read_data_from_excel():
  try:
    df = pd.read_html('Agmarknet_Price_And_Arrival_Report.xls')[0]
    return df
  except FileNotFoundError as e:
    print(f"File not found: {e}")
    sys.exit(1)
  except ValueError as e:
    print(f"Value error: {e}")
    sys.exit(1)

# Function to transform dataframe
def transform_data(df, commodity, time_agg):
  try:
    df.drop(df.tail(2).index, inplace=True) # Drop last two lines of sheet detailing total
    df.loc[:, "commodity"] = commodity # Add commodity column
    df.loc[:, 'date_arrival'] = pd.to_datetime(df['date_arrival']) # Type cast date to datetime

    # Rename columns so that it matches table columns
    df.columns = ["state", "district", "market", "com_variety", "com_group", "arrival", "min_price", "max_price", "modal_price", "date_arrival", "commodity"]

    # Determine group by time parameter based on time_agg
    if(time_agg == "daily"):
        frequency = "D"
    elif(time_agg == "yearly"):
        frequency = "AS"
    else:
        frequency = "MS" #Month Start

    result = df.groupby( [ "state", "district", "market", "com_variety", "com_group", pd.Grouper(key='date_arrival', freq=frequency), "commodity"] ).agg({"arrival":'mean', "min_price":'mean', "max_price":'mean', "modal_price":'mean'}).reset_index()
  
    return result
  except KeyError as e:
    print(f"Key error: {e}")
    sys.exit(1)
  except TypeError as e:
    print(f"Type error: {e}")
    sys.exit(1)

# Function to write dataframe to the database
def write_to_database(df):
  try:
    with psycopg2.connect(
        user = os.getenv("DB_USER"),
        password = os.getenv("DB_PWD"),
        host = os.getenv("DB_HOST"),
        port = os.getenv("DB_PORT"),
        database = os.getenv("DB_NAME")
    ) as connection:
      with connection.cursor() as cursor:
        print("Connected to the database successfully")
  except (Exception, psycopg2.Error) as error:
    print("Error while connecting to PostgreSQL", error)
    sys.exit(1)

  # No commit necessary since we're using SQLAlchemy. However, that might change based on engine.
  try:
    engine = create_engine(f'postgresql+psycopg2://{os.getenv("DB_USER")}:{os.getenv("DB_PWD")}@{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv("DB_NAME")}')

    df.to_sql(os.getenv("DB_TABLE"), engine, schema=os.getenv("DB_SCHEMA"), if_exists="append", index=False)
  except (Exception, SQLAlchemyError) as error:
    print("Error while writing to database", error)
    sys.exit(1)

  print("PostgreSQL connection is closed")
