"""Utilities for access databases, especially sqlite."""

import common_python.constants as cn

import os
import pandas as pd
import numpy as np
import sqlite3


def csvToTable(csv_path, db_path, tablename=None):
  """
  Write a CSV file as a table name, overwriting if exists.
  Deletes leading/trailing spaces. Replaces internal
  spaces with "_".
  :param str csv_path: path to the CSV file
  :param str db_path: path to the database
  :parm str tablename:
  """
  df = pd.read_csv(csv_path)
  conn = sqlite3.connect(db_path)
  if tablename is None:
    filename = os.path.split(csv_path)[1]
    tablename = os.path.splitext(filename)[0]
  columns = []
  for col in df.columns:
    new_col = col.strip()
    new_col = new_col.replace(" ", "_")
    columns.append(new_col)
  df.columns = columns
  df.to_sql(tablename, conn, if_exists='replace')

