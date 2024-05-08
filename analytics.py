### This class is built for the functions calls in the FastAPI ###
import pandas as pd
from adjustText import adjust_text
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
import warnings
from sklearn.exceptions import DataConversionWarning
import re

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

    # key used to sort bidding window string
    def bidding_window_sort_key(self, window):
        # Regular expression to extract round and window information
        match = re.search(r'(\d+[AB]?).*Window (\d+)', window)
        if match:
            # Convert the round part to a tuple of (number, sub-round), where sub-round is 'A' or 'B' or ''
            round_part = match.group(1)
            main_round = int(re.findall(r'\d+', round_part)[0])  # Main round number as integer
            sub_round = re.findall(r'[AB]', round_part)  # Sub-round letter if any
            sub_round = sub_round[0] if sub_round else ''  # Ensure sub-round is a single character or empty

            # Window number as integer
            window_number = int(match.group(2))

            # Check for special category "Incoming Freshmen"
            if 'Incoming Freshmen' in window:
                # Assign a lower precedence to incoming freshmen
                category = 1
            else:
                # Regular rounds have higher precedence
                category = 0
            
            return (category, main_round, sub_round, window_number)
        else:
            # If the pattern doesn't match, return a tuple that sorts the item last
            return (float('inf'),)

    # key used to sort Bidding Window string
    def term_sort_key(self, term):
        year, term_num = term.split(" Term ")
        return int(year.split("-")[0]), int(term_num)

    ### Getters Start ###
    def get_unique_faculties(self):
        return self.filtered_data["School/Department"].unique()
    
    def get_unique_course_codes(self):
        return self.filtered_data["Course Code"].unique()
    ### Getters End ###


    ### Filter Functions Start###
    def filter_by_course_code(self, course_code):
        """Returns df filtered by specified course_code"""
        course_code = course_code.upper()
        return self.filtered_data[self.filtered_data["Course Code"] == course_code]
    
    def filter_by_faculty(self, faculty):
        """Returns df filtered by specified course_code"""
        return self.filtered_data[self.filtered_data["Course Code"] == faculty]

    def filter_by_window(self, window):
        """Returns df filtered by specified course_code"""
        return self.filtered_data[self.filtered_data["Bidding Window"] == window]


    def filter_by_course_code_and_instructor(self, course_code, instructor_name):
        """Returns df filtered by specified course_code and instructor name"""
        course_code = course_code.upper()
        filtered_by_course_code = self.filter_by_course_code(course_code)
        return filtered_by_course_code[filtered_by_course_code["Instructor"].str.strip() == instructor_name.strip()]
    
    def filter_by_course_code_instructor_and_window(self, course_code, instructor_name, window):
        """Returns df filtered by specified course_code and instructor name"""
        course_code = course_code.upper()
        filtered_by_course_code = self.filter_by_course_code(course_code)
        filtered_by_instructor = filtered_by_course_code[filtered_by_course_code["Instructor"] == instructor_name.strip()]
        return filtered_by_instructor[filtered_by_instructor["Bidding Window"] == window]

    ### Filter Functions End###


    ### Get Instructors By Functions Start###  
    def get_instructors_by_course_code(self, course_code):
        """Input: Course Code\nOutput: array of distinct instructors"""
        course_code = course_code.upper()
        course_df = self.filter_by_course_code(course_code)
        return course_df["Instructor"].unique()
    
    def get_instructors_by_faculty(self, faculty):
        return self.filtered_data[faculty].unique()
    
    ### Get Instructors By Functions End ###


    ### Get Bidding Window By Functions Start ###  
    def get_bidding_windows_of_instructor_who_teach_course(self, course_code, instructor_name):
        course_code = course_code.upper()
        df = self.filter_by_course_code_and_instructor(course_code, instructor_name)
        return sorted(df["Bidding Window"].unique(), key=self.bidding_window_sort_key)


    ### Get Bidding Window By Functions End ###  


    ### Get Course Overview Start ###
    def get_min_max_median_mean_median_bid_values_by_course_code_and_instructor(self, course_code, instructor_name=None):
        """Returns the min, max, median, mean MEDIAN bid values for specified course code and instructor(if passed into args) in form of an array of:\n[min_median_value, max_median_value, median_median_value, mean_median_value]"""
        course_code = course_code.upper()
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
        course_code = course_code.upper()
        course_df = self.filter_by_course_code(course_code)
        title="Median 'Median Bid' Price (across all sections) against Instructors"
        x_axis_label=f"Instructors Teaching {course_code}"
        y_axis_label="Median 'Median Bid Price'"
        x_axis_data = []
        y_axis_data = []

        teaching_instructors = self.get_instructors_by_course_code(course_code)

        for instructor in teaching_instructors:
            median = round(course_df[course_df["Instructor"] == instructor]["Median Bid"].median(), 2)
            y_axis_data.append(median)
            x_axis_data.append(instructor)
        
        return [title, x_axis_label, x_axis_data, y_axis_label, y_axis_data]
    ### Get Course Overview End ###


    ### Get Line chart Data for Bid Price Trends Start ###
    def get_bid_price_data_by_course_code_and_window(self, course_code, window, instructor):
        course_code = course_code.upper()
        df = self.filter_by_course_code_instructor_and_window(course_code, instructor, window)
        title = "Median 'Median Bid' Price (across all sections) against Bidding Window"
        x_axis_label="Bidding Window"
        y_axis_label="Median 'Median Bid Price'"
        x_axis_data = []
        y_axis_data = []
        
        # IMPT to sort the terms
        terms_taught_for_specified_window = sorted(df["Term"].unique(), key=self.term_sort_key)
        
        for term in terms_taught_for_specified_window:
            term_median_median_bid = round(df[df["Term"] == term]["Median Bid"].median(), 2)
            x_axis_data.append(term)
            y_axis_data.append(term_median_median_bid)

        return [title, x_axis_label, x_axis_data, y_axis_label, y_axis_data]
    ### Get Line chart Data for Bid Price Trends End ###
  