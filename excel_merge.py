### This script merges the excel files in "./data" ###
import os
import pandas as pd
import openpyxl


def merge_excel_files(folder_path):
    excel_files = [filename for filename in os.listdir(folder_path)]
    entries = os.listdir(folder_path)

    for entry in entries:
        print(entry)

    column_mapping = {
        'Term': 'Term',
        'Session': 'Session',
        'Bidding Window': 'Bidding Window',
        'Course': 'Course Code',
        'Description': 'Description',  # Add this to retain description if needed
        'Sect': 'Section',
        'Median': 'Median Bid',
        'Min': 'Min Bid',
        'Vacancy': 'Vacancy',
        'Open': 'Opening Vacancy',
        'Bef Proc': 'Before Process Vacancy',
        'Aft Proc': 'After Process Vacancy',
        'DICE': 'D.I.C.E',
        'Enrolled': 'Enrolled Students',
        'Instructor': 'Instructor',
        'School': 'School/Department'
    }

    reference_columns = [
        'Term', 'Session', 'Bidding Window', 'Course Code', 'Description', 
        'Section', 'Vacancy', 'Opening Vacancy', 'Before Process Vacancy', 
        'D.I.C.E', 'After Process Vacancy', 'Enrolled Students', 
        'Median Bid', 'Min Bid', 'Instructor', 'School/Department'
    ]

    dfs = []

    for i, filename in enumerate(excel_files):
        if filename != ".DS_Store":
            file_path = os.path.join(folder_path, filename)
            df = pd.read_excel(file_path)
            df.rename(columns=column_mapping, inplace=True)
            df = df[reference_columns]
            if i == 0:
                dfs.append(df)
            else:
                
                dfs.append(df[1:])

    merged_df = pd.concat(dfs, ignore_index=True)
    output_path = "/Users/qingyuliu/PycharmProjects/bossanalytics/data/merged_file.xls"
    merged_df.to_excel(output_path, index=False, engine="openpyxl")


folder_path = "/Users/qingyuliu/PycharmProjects/bossanalytics/data"
merge_excel_files(folder_path)