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
            title="Course Min, Max, Median, Mean 'Median Bid' Price",
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
        [x_axisDataArr, y_axisDataArr] = analytics.get_all_instructor_median_median_bid_by_course_code(course_code.upper())
        response = OverviewCourseDataResponse(
            title="Median 'Median Bid' Price Across Instructors",
            x_axis_label=f"Instructors Teaching {course_code}",
            y_axis_label="Median 'Median Bid Price'",
            x_axis_values=x_axisDataArr,
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
            status_code=500,
            detail="Server Error"
        ) 