import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from analytics import Analytics

dataframe = pd.read_excel("data/merged_file.xls")
analytics = Analytics(dataframe)
valid_course_codes = analytics.get_unique_course_codes()
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    # specify domain name as only site we take requests from Eg. bosscharts.com
    allow_origins=[
        "https://bosscharts-git-main-qingyu255s-projects.vercel.app",
        "https://bosscharts-qingyu255s-projects.vercel.app",
        "http://bosscharts.vercel.app",
        "http://smubosscharts.com",
        "http://www.smubosscharts.com",
        "https://www.bosscharts.vercel.app",
        "https://www.smubosscharts.com",
        "https://www.smubosscharts.com",
        "http://localhost:3000",
        "https://localhost:3000"
    ],  # Allow requests from specified origin
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

class ReturnStringArr(BaseModel):
    data: List[str]

class ReturnDictionary(BaseModel):
    data: Dict[str, str]

class Dataset(BaseModel):
    label: str
    data: List[float]
    borderColor: str
    backgroundColor: str

class MultitypeDataset(BaseModel):
    type: str
    label: str
    data: List[float]
    borderColor: str
    backgroundColor: str
    yAxisID: str

class ReturnMultichartDatasetArr(BaseModel):
    data: List[MultitypeDataset]
    
class ChartData(BaseModel):
    responsive: bool
    labels: List[str]
    datasets: List[Dataset]

class CourseDataResponse(BaseModel):
    title: str
    chartData: ChartData


@app.get("/uniqueprofessors")
async def get_unique_professors():
    # returns string of course_code : course_name
    try:
        response = ReturnStringArr (
            data = analytics.get_unique_professors()
        )
        return response
    except Exception as e:
            raise HTTPException(
            status_code=500,
            detail="Server Error"
        )

@app.get("/uniquecourses")
async def get_unique_course_codes():
    # returns string of course_code : course_name
    try:
        response = ReturnStringArr (
            data = analytics.course_code_and_name_str_array
        )
        return response
    except Exception as e:
            raise HTTPException(
            status_code=500,
            detail="Server Error"
        ) 
    
@app.get("/coursename/{course_code}")
async def returnCourseNameByCourseCode(course_code):
    try:
        return analytics.get_course_name(course_code)
    except Exception as e:
            raise HTTPException(
            status_code=404,
            detail="course Not Found"
        )
    
@app.get("/coursestaughtbyprofessor/{instructor_name}")
async def returnCourseTaughtByProfessor(instructor_name):
    try:
        response = ReturnStringArr (
            data = analytics.get_courses_by_professor(instructor_name)
        )
        return response
    except Exception as e:
            raise HTTPException(
            status_code=404,
            detail="Not Found"
        )

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
            detail=str(e)
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
            detail=str(e)
        ) 

@app.get("/instructordata/sections_available/{course_code}/{instructor_name}/{selectedTerm}")
async def returnAvailableSections(course_code, instructor_name, selectedTerm):
    try:
        # pass in upper case!
        response = ReturnStringArr(
            data=analytics.get_sections_for_specific_course_instructor_term(course_code.upper(), instructor_name, selectedTerm)
        )
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )   
    
@app.get("/instructordata/terms_available/{course_code}/{instructor_name}")
async def returnAvailableTermsOfInstructorWhoTeachCourse(course_code, instructor_name):
    try:
        # pass in upper case!
        response = ReturnStringArr(
            data=analytics.get_terms_by_course_code_and_instructor(course_code.upper(), instructor_name)
        )
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.get("/coursedata/overview/{course_code}")
async def returnCourseOverviewData(course_code):
    """"Returns [Min, Max, Median, Mean] Median Bid Price"""
    # ALWAYS PASS IN UPPER CASE COURSE CODE!
    if course_code.upper() not in valid_course_codes:
        raise HTTPException(
            status_code=404,
            detail="Course Code Not Found"
        )
    try :
        y_axisDataArr = analytics.get_min_max_median_mean_median_bid_values_by_course_code_and_instructor(course_code.upper())
        response = CourseDataResponse(
            title="Overview (across all sections from AY 2019/20 onwards)",
            chartData= ChartData(
                responsive=True,
                labels=["Min 'median bid'", "Median 'median bid'", "Mean 'median bid'", "Max 'median bid'"],
                datasets=[{
                    "label": "Median Bid",
                    "data": y_axisDataArr,
                    "borderColor": "",
                    "backgroundColor": "rgba(41, 128, 185, 1)"
                }]
            )
        )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        ) 

@app.get("/coursedata/overview/instructor_median_bid_chart/{course_code}")
async def returnCourseInstructorOverviewData(course_code):
    """"Returns charting data in form of 2d array: [x_axis_data, y_axis_data]"""
    # ALWAYS PASS IN UPPER CASE COURSE CODE!
    try :
        [title, x_axis_data, median_median_bid_y_axis_data, mean_median_bid_y_axis_data] = analytics.get_all_instructor_median_and_mean_median_bid_by_course_code(course_code.upper())
        response = CourseDataResponse(
            title=title,
            chartData= ChartData(
                responsive=True,
                labels=x_axis_data,
                datasets=[{
                    "label": "Median 'Median Bid' price",
                    "data": median_median_bid_y_axis_data,
                    "borderColor": "",
                    "backgroundColor": "rgba(41, 128, 185, 1)"
                },
                {
                    "label": "Mean 'Median Bid' price",
                    "data": mean_median_bid_y_axis_data,
                    "borderColor": "",
                    "backgroundColor": "rgba(75, 192, 192, 1)"
                }]
            )
        )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        ) 
    
@app.get("/coursedata/bidpriceacrossterms/{course_code}/{window}/{instructor_name}")
async def returnBidPriceDataAcrossTermsForSpecifiedCourseAndWindow(course_code, window, instructor_name):
    try:
        [title, x_axis_data, y_axis_data] = analytics.get_bid_price_data_by_course_code_and_window_across_terms(course_code.upper(), window, instructor_name)
        response = CourseDataResponse(
            title=title,
            chartData= ChartData(
                responsive=True,
                labels=x_axis_data,
                datasets=[{
                    "label": "Median Bid",
                    "data": y_axis_data,
                    "borderColor": "rgba(75, 192, 192, 1)",
                    "backgroundColor": "rgba(41, 128, 185, 1)",
                }]
            )
        )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        ) 
    
@app.get("/coursedata/bidpriceacrosswindows/{course_code}/{term}/{instructor_name}")
async def returnBidPriceDataAcrossWindowsForSpecifiedCourseAndTerm(course_code, term, instructor_name):
    try:
        [title, x_axis_data, y_axis_data] = analytics.get_bid_price_data_by_course_code_and_term_across_windows(course_code, term, instructor_name)
        response = CourseDataResponse(
            title=title,
            chartData= ChartData(
                responsive=True,
                labels=x_axis_data,
                datasets=[{
                    "label": "Median Bid",
                    "data": y_axis_data,
                    "borderColor": "rgba(75, 192, 192, 1)",
                    "backgroundColor": "rgba(41, 128, 185, 1)",
                }]
            )
        )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    
@app.get("/coursedata/sectionbidpriceacrosswindows/{course_code}/{term}/{instructor_name}/{section}")
async def returnBidPriceDataAcrossWindowsForSpecifiedCourseAndTerm(course_code, term, instructor_name, section):
    try:
        [title, x_axis_data, y_axis_data_median_bid, y_axis_data_min_bid] = analytics.get_bid_price_data_by_course_code_term_and_section_across_windows(course_code, term, instructor_name, section)
        response = CourseDataResponse(
            title=title,
            chartData= ChartData(
                responsive=True,
                labels=x_axis_data,
                datasets=[{
                    "label": "Median Bid",
                    "data": y_axis_data_median_bid,
                    "borderColor": "rgba(75, 192, 192, 1)",
                    "backgroundColor": "rgba(41, 128, 185, 1)",
                },
                {
                    "label": "Min Bid",
                    "data": y_axis_data_min_bid,
                    "borderColor": "rgba(75, 50, 192, 1)",
                    "backgroundColor": "rgba(41, 128, 185, 1)",
                }]
            )
        )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.get("/coursedata/bidpriceacrossterms/vacancies/{course_code}/{window}/{instructor_name}")
async def returnBeforeAfterVacanciesForCourseAndWindowOverTerm(course_code, window, instructor_name):
    try:
        [y_axis_data_before_vacancies, y_axis_data_after_vacancies] = analytics.get_before_after_vacancies_by_course_code_and_window_across_terms(course_code, window, instructor_name)
        response = ReturnMultichartDatasetArr(data = [
            MultitypeDataset(
                # type is lowercase
                type = "bar",
                label = "Before Process Vacancies",
                data = y_axis_data_before_vacancies,
                borderColor = "rgb(255, 99, 132)",
                backgroundColor = "rgba(255, 99, 132, 0.2)",
                fill = False,
                yAxisID = 'y1'
            ),
            MultitypeDataset(
                type = "bar",
                label = "After Process Vacancies",
                data = y_axis_data_after_vacancies,
                borderColor = "rgb(53, 162, 235)",
                backgroundColor = "rgba(53, 162, 235, 0.2)",
                yAxisID = 'y1',
            )
        ])
        return response
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    

@app.get("/coursedata/bidpriceacrosswindows/vacancies/{course_code}/{term}/{instructor_name}")
async def returnBeforeAfterVacanciesForCourseAndTermOverWindow(course_code, term, instructor_name):
    try:
        [y_axis_data_before_vacancies, y_axis_data_after_vacancies] = analytics.get_before_after_vacancies_by_course_code_and_term_across_windows(course_code, term, instructor_name)
        response = ReturnMultichartDatasetArr(data = [
            MultitypeDataset(
                # type is lowercase
                type = "bar",
                label = "Before Process Vacancies",
                data = y_axis_data_before_vacancies,
                borderColor = "rgb(255, 99, 132)",
                backgroundColor = "rgba(255, 99, 132, 0.2)",
                fill = False,
                yAxisID = 'y1'
            ),
            MultitypeDataset(
                type = "bar",
                label = "After Process Vacancies",
                data = y_axis_data_after_vacancies,
                borderColor = "rgb(53, 162, 235)",
                backgroundColor = "rgba(53, 162, 235, 0.2)",
                yAxisID = 'y1',
            )
        ])
        return response
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    
@app.get("/coursedata/sectionbidpriceacrosswindows/vacancies/{course_code}/{term}/{instructor_name}/{section}")
async def returnBeforeAfterVacanciesForCourseTermAndSectionOverWindow(course_code, term, instructor_name, section):
    try:
        [y_axis_data_before_vacancies, y_axis_data_after_vacancies] = analytics.get_before_after_vacancies_by_course_code_term_and_section_across_windows(course_code, term, instructor_name, section)
        response = ReturnMultichartDatasetArr(data = [
            MultitypeDataset(
                # type is lowercase
                type = "bar",
                label = "Before Process Vacancies",
                data = y_axis_data_before_vacancies,
                borderColor = "rgb(255, 99, 132)",
                backgroundColor = "rgba(255, 99, 132, 0.2)",
                fill = False,
                yAxisID = 'y1'
            ),
            MultitypeDataset(
                type = "bar",
                label = "After Process Vacancies",
                data = y_axis_data_after_vacancies,
                borderColor = "rgb(53, 162, 235)",
                backgroundColor = "rgba(53, 162, 235, 0.2)",
                yAxisID = 'y1',
            )
        ])
        return response
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )