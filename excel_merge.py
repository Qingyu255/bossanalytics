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
        # skip hidden files like .DS_Store
        if filename.startswith('.'):
            continue

        file_path = os.path.join(folder_path, filename)
        ext = os.path.splitext(filename)[1].lower()

        try:
            if ext == '.csv':
                df = pd.read_csv(file_path)
            elif ext in ['.xls', '.xlsx']:
                # specify engine for xlsx; let pandas choose for xls
                if ext == '.xlsx':
                    df = pd.read_excel(file_path, engine='openpyxl')
                else:
                    df = pd.read_excel(file_path)
            else:
                print(f"Skipping unsupported file type: {filename}")
                continue
        except Exception as e:
            print(f"Failed to read {filename}: {e}")
            continue

        df.rename(columns=column_mapping, inplace=True)

        # ensure all reference columns exist
        for col in reference_columns:
            if col not in df.columns:
                df[col] = pd.NA

        df = df[reference_columns]

        # preserve previous behavior: skip the header row for subsequent files
        if len(dfs) == 0:
            dfs.append(df)
        else:
            dfs.append(df[1:])

    merged_df = pd.concat(dfs, ignore_index=True)
    output_path = "/Users/qingyuliu/PycharmProjects/bossanalytics/data/merged_file.xlsx"
    merged_df.to_excel(output_path, index=False, engine="openpyxl")


folder_path = "/Users/qingyuliu/PycharmProjects/bossanalytics/data"
merge_excel_files(folder_path)