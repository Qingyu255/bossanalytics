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

        course_codes = self.filtered_data["Course Code"].to_list()
        course_names = self.filtered_data["Description"].to_list()
        course_code_and_name_str_array = []
        unique_course_code_to_course_name_map = {}
        for i in range(len(course_codes)):
            if course_codes[i] not in unique_course_code_to_course_name_map:
                if course_codes[i] == "COR3001":
                    unique_course_code_to_course_name_map[course_codes[i]] = "Big Questions"
                else:
                    unique_course_code_to_course_name_map[course_codes[i]] = course_names[i]
                course_code_and_name_str_array.append(course_codes[i] + ": " + course_names[i])
        self.unique_course_code_to_course_name_map = unique_course_code_to_course_name_map
        self.course_code_and_name_str_array = course_code_and_name_str_array

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
    def get_unique_professors(self):
        return self.filtered_data["Instructor"].unique()
    
    def get_unique_faculties(self):
        return self.filtered_data["School/Department"].unique()
    
    def get_unique_course_codes(self):
        return self.filtered_data["Course Code"].unique()
    
    def get_course_name(self, course_code):
        course_code = course_code.upper()
        return self.unique_course_code_to_course_name_map[course_code]
    ### Getters End ###


    ### Filter Functions Start###
    def filter_by_course_code(self, course_code):
        """Returns df filtered by specified course_code"""
        course_code = course_code.upper()
        return self.filtered_data[self.filtered_data["Course Code"] == course_code]
    
    def filter_by_faculty(self, faculty):
        """Returns df filtered by specified faculty"""
        return self.filtered_data[self.filtered_data["Course Code"] == faculty]

    def filter_by_window(self, window):
        """Returns df filtered by specified window"""
        return self.filtered_data[self.filtered_data["Bidding Window"] == window]

    def filter_by_term(self, term):
        """Returns df filtered by specified term"""
        return self.filtered_data[self.filtered_data["Term"] == term]

    def filter_by_course_code_and_instructor(self, course_code, instructor_name):
        """Returns df filtered by specified course_code and instructor name"""
        course_code = course_code.upper()
        filtered_by_course_code = self.filter_by_course_code(course_code)
        return filtered_by_course_code[filtered_by_course_code["Instructor"].str.strip() == instructor_name.strip()]
    
    def filter_by_course_code_instructor_and_window(self, course_code, instructor_name, window):
        """Returns df filtered by specified course_code, instructor name and window"""
        course_code = course_code.upper()
        filtered_by_course_code = self.filter_by_course_code(course_code)
        filtered_by_instructor = filtered_by_course_code[filtered_by_course_code["Instructor"] == instructor_name.strip()]
        return filtered_by_instructor[filtered_by_instructor["Bidding Window"] == window]

    def filter_by_course_code_instructor_and_term(self, course_code, instructor_name, term):
        course_code = course_code.upper()
        filtered_by_course_code = self.filter_by_course_code(course_code)
        filtered_by_instructor = filtered_by_course_code[filtered_by_course_code["Instructor"] == instructor_name.strip()]
        return filtered_by_instructor[filtered_by_instructor["Term"] == term]
        
    ### Filter Functions End###

    ### Get Instructors By Functions Start###  
    def get_terms_by_course_code_and_instructor(self, course_code, instructor_name):
        filtered_by_course_code = self.filter_by_course_code(course_code)
        filtered_by_instructor = filtered_by_course_code[filtered_by_course_code["Instructor"] == instructor_name.strip()]
        return sorted(filtered_by_instructor["Term"].unique(), key=self.term_sort_key, reverse=True)

    def get_instructors_by_course_code(self, course_code):
        """Input: Course Code\nOutput: array of distinct instructors"""
        course_code = course_code.upper()
        course_df = self.filter_by_course_code(course_code)
        return course_df["Instructor"].unique()
    
    def get_instructors_by_faculty(self, faculty):
        return self.filtered_data[faculty].unique()
    
    def get_courses_by_professor(self, instructor_name):
        filtered_by_instructor = self.filtered_data[self.filtered_data["Instructor"] == instructor_name.upper().strip()]
        unique_courses = filtered_by_instructor["Course Code"].unique()

        res = []
        for course_code in unique_courses:
            res.append(course_code + ": " + self.unique_course_code_to_course_name_map[course_code])
        return res
    ### Get Instructors By Functions End ###


    ### Get Bidding Window By Functions Start ###  
    def get_bidding_windows_of_instructor_who_teach_course(self, course_code, instructor_name):
        course_code = course_code.upper()
        df = self.filter_by_course_code_and_instructor(course_code, instructor_name)
        return sorted(df["Bidding Window"].unique(), key=self.bidding_window_sort_key)
    ### Get Bidding Window By Functions End ###  

    def get_sections_for_specific_course_instructor_term(self, course_code, instructor_name, term):
        course_code = course_code.upper()
        df = self.filter_by_course_code_and_instructor(course_code, instructor_name)
        df = df[df["Term"] == term]
        return sorted(df["Section"].unique())


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
        return [min_median_value, median_median_value, mean_median_value, max_median_value]
    
    def get_all_instructor_median_and_mean_median_bid_by_course_code(self, course_code):
        """returns 2d array containing x_axis_data array and y_axis_data array"""
        course_code = course_code.upper()
        course_df = self.filter_by_course_code(course_code)
        title="Median and Mean 'Median Bid' Price (across all sections) against Instructors"
        x_axis_data = []
        median_median_bid_y_axis_data = []
        mean_median_bid_y_axis_data = []

        teaching_instructors = self.get_instructors_by_course_code(course_code)

        for instructor in teaching_instructors:
            series = course_df[course_df["Instructor"] == instructor]["Median Bid"]
            median = round(series.median(), 2)
            median_median_bid_y_axis_data.append(median)

            mean = round(series.mean(), 2)
            mean_median_bid_y_axis_data.append(mean)
            x_axis_data.append(instructor)
        return [title, x_axis_data, median_median_bid_y_axis_data, mean_median_bid_y_axis_data]
    ### Get Course Overview End ###


    ### Get Line chart Data for Bid Price Trends Start ###
    def get_bid_price_data_by_course_code_and_window_across_terms(self, course_code, window, instructor):
        course_code = course_code.upper()
        df = self.filter_by_course_code_instructor_and_window(course_code, instructor, window)
        title = "Median 'Median Bid' Price (across all sections) against Term"
        x_axis_data = []
        y_axis_data = []
        
        # IMPT to sort the terms
        terms_taught_for_specified_window = sorted(df["Term"].unique(), key=self.term_sort_key)
        
        for term in terms_taught_for_specified_window:
            term_median_median_bid = round(df[df["Term"] == term]["Median Bid"].median(), 2)
            x_axis_data.append(term)
            y_axis_data.append(term_median_median_bid)

        return [title, x_axis_data, y_axis_data]
    
    def get_bid_price_data_by_course_code_and_term_across_windows(self, course_code, term, instructor):
        course_code = course_code.upper()
        df = self.filter_by_course_code_instructor_and_term(course_code, instructor, term)
        title = f"Median 'Median Bid' Price (across all sections) against Bidding Window for {term}"
        x_axis_data = []
        y_axis_data = []
        
        # IMPT to sort the terms
        windows_for_specified_term = sorted(df["Bidding Window"].unique(), key=self.bidding_window_sort_key)
        
        for window in windows_for_specified_term:
            window_median_median_bid = round(df[df["Bidding Window"] == window]["Median Bid"].median(), 2)
            x_axis_data.append(window)
            y_axis_data.append(window_median_median_bid)

        return [title, x_axis_data, y_axis_data]
    
    def get_bid_price_data_by_course_code_term_and_section_across_windows(self, course_code, term, instructor, section):
        course_code = course_code.upper()
        df = self.filter_by_course_code_instructor_and_term(course_code, instructor, term)
        df = df[df["Section"] == section]
        title = f"Median, Min Bid Price against Bidding Window for {term}, Section {section}"
        x_axis_data = []
        y_axis_data_median_bid = []
        y_axis_data_min_bid = []
        
        # IMPT to sort the terms
        windows_for_specified_term = sorted(df["Bidding Window"].unique(), key=self.bidding_window_sort_key)
        
        for window in windows_for_specified_term:
            median_bid = df[df["Bidding Window"] == window]["Median Bid"]
            min_bid = df[df["Bidding Window"] == window]["Min Bid"]
            x_axis_data.append(window)
            y_axis_data_median_bid.append(median_bid)
            y_axis_data_min_bid.append(min_bid)

        return [title, x_axis_data, y_axis_data_median_bid, y_axis_data_min_bid]
    ### Get Line chart Data for Bid Price Trends End ###


    ### Get MultitypeChart Extra DataArr Start ### 
    def get_before_after_vacancies_by_course_code_and_window_across_terms(self, course_code, window, instructor, filter_by_section=""):
        course_code = course_code.upper()
        df = self.filter_by_course_code_instructor_and_window(course_code, instructor, window)
        if filter_by_section != "":
            df = df[df["Section"] == filter_by_section]
        terms_taught = sorted(df["Term"].unique(), key=self.term_sort_key)
        
        y_axis_data_before_vacancies = []
        y_axis_data_after_vacancies = []
        for term in terms_taught:
            term_df = df[df["Term"] == term]
            term_before_process_vacancies = term_df["Before Process Vacancy"].sum()
            term_after_process_vacancies = term_df["After Process Vacancy"].sum()
            y_axis_data_before_vacancies.append(term_before_process_vacancies)
            y_axis_data_after_vacancies.append(term_after_process_vacancies)
        return [y_axis_data_before_vacancies, y_axis_data_after_vacancies]


    def get_before_after_vacancies_by_course_code_and_term_across_windows(self, course_code, term, instructor):
        course_code = course_code.upper()
        df = self.filter_by_course_code_instructor_and_term(course_code, instructor, term)

        windows = sorted(df["Bidding Window"].unique(), key=self.bidding_window_sort_key)
        
        y_axis_data_before_vacancies = []
        y_axis_data_after_vacancies = []
        for window in windows:
            window_df = df[df["Bidding Window"] == window]
            window_before_process_vacancies = window_df["Before Process Vacancy"].sum()
            window_after_process_vacancies = window_df["After Process Vacancy"].sum()
            y_axis_data_before_vacancies.append(window_before_process_vacancies)
            y_axis_data_after_vacancies.append(window_after_process_vacancies)
        return [y_axis_data_before_vacancies, y_axis_data_after_vacancies]

    def get_before_after_vacancies_by_course_code_term_and_section_across_windows(self, course_code, term, instructor, section):
        course_code = course_code.upper()
        df = self.filter_by_course_code_instructor_and_term(course_code, instructor, term)
        df = df[df["Section"] == section]

        windows = sorted(df["Bidding Window"].unique(), key=self.bidding_window_sort_key)
        
        y_axis_data_before_vacancies = []
        y_axis_data_after_vacancies = []
        for window in windows:
            window_df = df[df["Bidding Window"] == window]
            window_before_process_vacancies = window_df["Before Process Vacancy"].sum()
            window_after_process_vacancies = window_df["After Process Vacancy"].sum()
            y_axis_data_before_vacancies.append(window_before_process_vacancies)
            y_axis_data_after_vacancies.append(window_after_process_vacancies)
        return [y_axis_data_before_vacancies, y_axis_data_after_vacancies]
    ### Get MultitypeChart Extra DataArr End ### 
  