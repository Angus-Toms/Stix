"""
Functions used by various classes of the Detailed Appraisal
"""


import csv
from typing import List

import pandas as pd
from dbfread import DBF
from PyQt5.QtWidgets import (QAbstractItemView, QHeaderView, QTableWidget,
                             QTableWidgetItem)


def table_from_csv(fname: List[str]) -> QTableWidget:
    """
    Build .csv data into a QTableWidget
    """
    data = []
    # Read csv to 2d list
    with open(fname[0]) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            data.append(row)

    # Build and populate table
    table = QTableWidget()

    # Catch blank csvs
    try:
        rowCount = len(data)
        colCount = len(data[0])
    except:
        rowCount, colCount = 0, 0

    table.setRowCount(rowCount)
    table.setColumnCount(colCount)

    for row in range(rowCount):
        for col in range(colCount):
            cell = QTableWidgetItem(data[row][col])
            table.setItem(row, col, cell)

    table.resizeColumnsToContents()

    return table


def table_from_dbf(fname: List[str]) -> QTableWidget:
    """      
    Build .dbf data into a QTableWidget
    """
    # Read dbf to 2d list
    df = pd.DataFrame(iter(DBF(fname[0])))
    headings = list(df.columns.values)

    data = [[str(datapoint) for datapoint in row.tolist()]
            for _, row in df.iterrows()]

    # Build and populate table
    table = QTableWidget()

    # Catch blank dbfs
    try:
        rowCount = len(data)
        colCount = len(data[0])
    except:
        rowCount, colCount = 0, 0

    table.setRowCount(rowCount)
    table.setColumnCount(colCount)
    table.setHorizontalHeaderLabels(
        [f"{i+1} - {headings[i]}" for i in range(len(headings))])

    for row in range(rowCount):
        for col in range(colCount):
            cell = QTableWidgetItem(data[row][col])
            table.setItem(row, col, cell)

    table.resizeColumnsToContents()

    return table


def table_from_list(headings: List[str], dataset: List[List[str]]) -> QTableWidget:
    """
    Create a table from a 2d list with custom headings 
    """
    table = QTableWidget()
    row_count = len(dataset)
    col_count = len(headings)
    table.setRowCount(row_count)
    table.setColumnCount(col_count)

    # Create items from dataset and insert into table widget
    for row in range(row_count):
        for col in range(col_count):
            item = QTableWidgetItem(dataset[row][col])
            table.setItem(row, col, item)

    # Set table headings
    table.setHorizontalHeaderLabels(headings)

    # Turn off editing
    table.setEditTriggers(QAbstractItemView.NoEditTriggers)

    # Size adjusments and formatting
    header = table.horizontalHeader()
    header.setSectionResizeMode(QHeaderView.Stretch)

    return table


def read_table_with_columns(columns: List[int], table: QTableWidget) -> List[List]:
    """
    Read cells from table from given columns 
    """
    dataset = []
    for r in range(table.rowCount()):
        row = []
        for c in columns:
            # Catch blank cells
            try:
                cell = table.item(r, c-1)
                row.append(cell.text())
            except:
                row.append(None)

        dataset.append(row)

    return dataset

