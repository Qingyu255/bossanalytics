### This script merges the excel files in "./data" ###
import os
import pandas as pd
import openpyxl


def merge_excel_files(folder_path):
    excel_files = [filename for filename in os.listdir(folder_path)]
    entries = os.listdir(folder_path)

    for entry in entries:
        print(entry)

    dfs = []
    for i, filename in enumerate(excel_files):
        if filename != ".DS_Store":
            file_path = os.path.join(folder_path, filename)
            df = pd.read_excel(file_path, engine="xlrd")
            if i == 0:
                dfs.append(df)
            else:
                dfs.append(df[1:])

    merged_df = pd.concat(dfs, ignore_index=True)
    output_path = "/Users/qingyuliu/PycharmProjects/bossanalytics/data/merged_file.xls"
    merged_df.to_excel(output_path, index=False, engine="openpyxl")


folder_path = "/Users/qingyuliu/PycharmProjects/bossanalytics/data"
merge_excel_files(folder_path)