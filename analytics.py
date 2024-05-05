### This class is built for the functions calls in the FastAPI ###
import pandas as pd
from adjustText import adjust_text
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
import warnings
from sklearn.exceptions import DataConversionWarning

class Analytics:
    def __init__(self, data_frame) -> None:
        ### preprocess data in initialisation of class ###

        # Handling missing data: Remove rows with "Median Bid" equal to 0 or empty "Instructor" column
        filtered_data = data_frame.drop(data_frame[(data_frame["Median Bid"] == 0) | (data_frame["Instructor"].fillna("") == "") | (data_frame["Session"] != "Regular Academic Session")].index)
        filtered_data["round_successful_bids"] = filtered_data["Before Process Vacancy"] - filtered_data["After Process Vacancy"]

        # Strip the 'Instructor' and 'Course' values for better data integrity
        filtered_data["Instructor"] = filtered_data["Instructor"].str.strip()
        filtered_data["Course Code"] = filtered_data["Course Code"].str.strip()

        # Delete unnecessary columns
        cols_to_delete = ["D.I.C.E"]
        filtered_data.drop(columns=cols_to_delete, inplace=True)

        self.filtered_data = filtered_data

    ### Getters Start ###
    def get_unique_faculties(self):
        return self.filtered_data["School/Department"].unique()
    
    def get_unique_course_codes(self):
        return self.filtered_data["Course Code"].unique()
    ### Getters End ###

    ### Filter Functions Start###
    def filter_by_course_code(self, course_code):
        """Returns df filtered by specified course_code"""
        return self.filtered_data[self.filtered_data["Course Code"] == course_code]
    
    def filter_by_faculty(self, faculty):
        """Returns df filtered by specified course_code"""
        return self.filtered_data[self.filtered_data["Course Code"] == course_code]

    def filter_by_course_code_and_instructor(self, course_code, instructor_name):
        """Returns df filtered by specified course_code and instructor name"""
        filtered_by_course_code = self.filter_by_course_code(course_code)
        return filtered_by_course_code[filtered_by_course_code["Instructor"].str.strip() == instructor_name.strip()]
    ### Filter Functions End###


    ### Get Instructors By Functions Start###  
    def get_instructors_by_course_code(self, course_code):
        """Input: Course Code\nOutput: array of distinct instructors"""
        course_df = self.filter_by_course_code(course_code)
        return course_df["Instructor"].unique()
    
    def get_instructors_by_faculty(self, faculty):
        return self.filtered_data[faculty].unique()
    
    ### Get Instructors By Functions End ###


    ### Get Course Overview Start ###
    def get_min_max_median_mean_median_bid_values_by_course_code_and_instructor(self, course_code, instructor_name=None):
        """Returns the min, max, median, mean MEDIAN bid values for specified course code and instructor(if passed into args) in form of an array of:\n[min_median_value, max_median_value, median_median_value, mean_median_value]"""
        if instructor_name:
            course_df = self.filter_by_course_code_and_instructor(course_code, instructor_name)
        else:
            course_df = self.filter_by_course_code(course_code)
        min_median_value = course_df["Median Bid"].min()
        max_median_value = course_df["Median Bid"].max()
        median_median_value = round(course_df["Median Bid"].median(), 2)
        mean_median_value = round(course_df["Median Bid"].mean(), 2)
        return [min_median_value, max_median_value, median_median_value, mean_median_value]
    
    def get_all_instructor_median_median_bid_by_course_code(self, course_code):
        """returns 2d array containing x_axis_data array and y_axis_data array"""
        teaching_instructors = self.get_instructors_by_course_code(course_code)
        course_df = self.filter_by_course_code(course_code)
        x_axis_data = []
        y_axis_data = []
        for instructor in teaching_instructors:
            median = round(course_df[course_df["Instructor"] == instructor]["Median Bid"].median(), 2)
            y_axis_data.append(median)
            x_axis_data.append(instructor)
        return [x_axis_data, y_axis_data]

    ### Get Course Overview End ###
  