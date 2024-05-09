import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from analytics import Analytics

dataframe = pd.read_excel("data/merged_file.xls")
analytics = Analytics(dataframe)
valid_course_codes = analytics.get_unique_course_codes()
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow requests from specified origin
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

class ReturnStringArr(BaseModel):
    data: List[str]

class Dataset(BaseModel):
    data: List[float]
    backgroundColor: str
    borderColor: str
    borderWidth: int

class OverviewCourseDataResponse(BaseModel):
    title: str
    x_axis_label: str
    y_axis_label: str
    x_axis_values: List[str]
    datasets: List[Dataset]


@app.get("/")
async def root():
    return {
        "Hello":"World"
    }

@app.get("/instructordata/instructor/{course_code}")
async def returnInstructorsWhoTeachCourse(course_code):
    try:
        # pass in upper case!
        response = ReturnStringArr(
            data=analytics.get_instructors_by_course_code(course_code.upper())
        )
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Server Error"
        ) 
    
@app.get("/instructordata/bidding_windows_available/{course_code}/{instructor_name}")
async def returnAvailableBiddingWindowsOfInstructorWhoTeachCourse(course_code, instructor_name):
    try:
        # pass in upper case!
        response = ReturnStringArr(
            data=analytics.get_bidding_windows_of_instructor_who_teach_course(course_code.upper(), instructor_name)
        )
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Server Error"
        ) 
    
@app.get("/coursedata/overview/{course_code}")
async def returnCourseOverviewData(course_code):
    """"Returns [Min, Max, Median, Mean] Median Bid Price"""
    # ALWAYS PASS IN UPPER CASE COURSE CODE!
    if course_code.upper() not in valid_course_codes:
        raise HTTPException(
            status_code=404,
            detail="course not found"
        )
    try :
        y_axisDataArr = analytics.get_min_max_median_mean_median_bid_values_by_course_code_and_instructor(course_code.upper())
        response = OverviewCourseDataResponse(
            title="",
            x_axis_label="Bidding Window",
            y_axis_label="Bid Price",
            x_axis_values=["Min 'median bid'", "Max 'median bid'", "Median 'median bid'", "Mean 'median bid'"],
            datasets=[
                Dataset(
                    data=y_axisDataArr,
                    backgroundColor="rgba(75, 192, 192, 0.6)",
                    borderColor="rgba(75, 192, 192, 1)",
                    borderWidth=2,
                )
            ]
        )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail="course not found"
        ) 

@app.get("/coursedata/overview/instructor_median_bid_chart/{course_code}")
async def returnCourseInstructorOverviewData(course_code):
    """"Returns charting data in form of 2d array: [x_axis_data, y_axis_data]"""
    # ALWAYS PASS IN UPPER CASE COURSE CODE!
    try :
        [title, x_axis_label, x_axis_data, y_axis_label, y_axis_data] = analytics.get_all_instructor_median_median_bid_by_course_code(course_code.upper())
        response = OverviewCourseDataResponse(
            title=title,
            x_axis_label=x_axis_label,
            y_axis_label=y_axis_label,
            x_axis_values=x_axis_data,
            datasets=[
                Dataset(
                    data=y_axis_data,
                    backgroundColor="rgba(75, 192, 192, 0.6)",
                    borderColor="rgba(75, 192, 192, 1)",
                    borderWidth=2,
                )
            ]
        )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Server Error"
        ) 
    
@app.get("/coursedata/bidpriceacrossterms/{course_code}/{window}/{instructor_name}")
async def returnBidPriceDataAcrossTermsForSpecifiedCourseAndWindow(course_code, window, instructor_name):
    try:
        [title, x_axis_label, x_axis_data, y_axis_label, y_axis_data] = analytics.get_bid_price_data_by_course_code_and_window_across_terms(course_code.upper(), window, instructor_name)
        response = OverviewCourseDataResponse(
            title=title,
            x_axis_label=x_axis_label,
            y_axis_label=y_axis_label,
            x_axis_values=x_axis_data,
            datasets=[
                Dataset(
                    data=y_axis_data,
                    backgroundColor="rgba(75, 192, 192, 0.6)",
                    borderColor="rgba(75, 192, 192, 1)",
                    borderWidth=2,
                )
            ]
        )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Server Error"
        ) 
    
@app.get("/coursedata/bidpriceacrosswindows/{course_code}/{term}/{instructor_name}")
async def returnBidPriceDataAcrossWindowsForSpecifiedCourseAndTerm(course_code, term, instructor_name):
    try:
        [title, x_axis_label, x_axis_data, y_axis_label, y_axis_data] = analytics.get_bid_price_data_by_course_code_and_term_across_windows(course_code.upper(), term, instructor_name)
        response = OverviewCourseDataResponse(
            title=title,
            x_axis_label=x_axis_label,
            y_axis_label=y_axis_label,
            x_axis_values=x_axis_data,
            datasets=[
                Dataset(
                    data=y_axis_data,
                    backgroundColor="rgba(75, 192, 192, 0.6)",
                    borderColor="rgba(75, 192, 192, 1)",
                    borderWidth=2,
                )
            ]
        )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Server Error"
        ) 