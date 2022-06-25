import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
import openpyxl
from functions import calcFreeLunch, loadSTEMData, loadDOEData, loadGraphData, TitleOne, Magnet, AllSchools, calcRetentionDisp, calcCRetentionDisp, calcRace, introCourses, yearFilter, introCourseRace, nonIntroCourses, calcBlackWomen, martin, t1Filter

#App Config
st.set_page_config(page_title="Broward STEM Data Analysis",
 page_icon="📊", layout="centered", initial_sidebar_state='auto')

# Years of data being analyzed
yearList = ['2014', '2015', '2016', '2017', '2018', '2019', '2020', '2021']

# Title
st.title('Broward STEM Data')
st.text("All students in BCPS taking STEM Classes 2014-2021")

# Load Data
data = loadSTEMData()
DOE_data = loadDOEData()

#Choose what years to analyze
years = st.multiselect("Years to Analyze", yearList, yearList)
if(len(years) == 0):
	st.text("Please select years to analyze.")
else:
	#Filter by years selected
	data = yearFilter(data, years, yearList)

	#Offer to sort only Title I schools
	titleOneMode = st.radio("Analyze:", ('All Schools', 'Title I Schools', 'Non Title I'))

	#Sort by Title I if requested
	data = t1Filter(data, DOE_data, titleOneMode)

	#Remove Title I or non Title I schools from DOE Data
	if (titleOneMode == 'Title I Schools'):
		DOE_data = DOE_data.loc[(DOE_data['School-wide Title I'] == "Yes")]

	if (titleOneMode == 'Non Title I'):
		DOE_data = DOE_data.loc[(DOE_data['School-wide Title I'] == "No")]

	#Load Graph Data based on what DOE data was filtered
	graph_data = loadGraphData(data, DOE_data, years)

	#Sidebar
	title = st.sidebar.markdown("## Menu")
	browse = st.sidebar.markdown("[Browse Data](#raw-data)")
	search = st.sidebar.markdown("[School Search](#school-search)")
	graphs = st.sidebar.markdown("[Graphs](#graphs)")
	corr = st.sidebar.markdown("[Correlations](#correlations)")
	schoolTA = st.sidebar.markdown("[School Type Analysis](#school-type-analysis)")

	#Sidebar width hack
	st.markdown(
    """
    <style>
    [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
        width: 250px;
    }
    [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
        width: 250px;
        margin-left: -500px;
    }
    </style>
    """,
    unsafe_allow_html=True
	)

	# Show Raw Data
	st.subheader('Raw Data')
	if(st.checkbox("Show Data")):
		st.write(data)

	#Group to browse sex data by school
	sex_data = data.groupby(["School"])["Sex"].value_counts()

	st.subheader('School and Gender Breakdown')
	if(st.checkbox("Show Breakdown")):
		sex_data

	#Search data by school
	st.subheader("School Search")
	selected_school = st.selectbox("Select School", DOE_data["School Name"].unique())
	selected_row = DOE_data[DOE_data['School Name'].str.contains(selected_school)]

	selected_row = selected_row.to_numpy()

	st.text("Magnet: " + selected_row[0][2])
	st.text("Title I: " + selected_row[0][3] + " (School Wide)")
	st.text("White: " + str(round((selected_row[0][8] / selected_row[0][4])* 100, 2)) + "%")
	st.text("Hispanic: " + str(round((selected_row[0][6] / selected_row[0][4])* 100, 2)) + "%")
	st.text("Black: " + str(round((selected_row[0][7] / selected_row[0][4])* 100, 2)) + "%")
	st.text("Free Lunch Eligible: " + str(round((selected_row[0][5] / selected_row[0][4])* 100, 2)) + "%")

	#Sex Data Extraction
	sex_data_arr = np.array(sex_data)

	#Ignore lines 48-50 ;)
	temp = sex_data_arr[0]
	sex_data_arr[0] = sex_data_arr[1]
	sex_data_arr[1] = temp

	index = DOE_data[DOE_data["School Name"] == selected_school].index.values

	male = sex_data_arr[index*2][0]
	female = sex_data_arr[index*2 + 1][0]

	st.text("Males per Female Student: " + str(round(male/female, 2)))

	st.text("The average male student took " + str(calcRetentionDisp(selected_school, data)) + " times the STEM courses")
	st.text("than the average female student")

	#Graphs of data
	st.subheader("Graphs")
	#st.text("How much does a school's socioeconomic status correlate with the gender diversity of their STEM program?")
	st.text("Free Lunch vs. sRatio")
	lunchSexGraph = alt.Chart(graph_data).mark_circle().encode(
		x='% Free Lunch',
		y='sRatio',
		tooltip=['School Name', '% Free Lunch', 'sRatio'])

	lunchSexGraph + lunchSexGraph.transform_regression('% Free Lunch', 'sRatio', method="poly").mark_line()
	
	#st.text("How much does a school's racial diversity correlate with the gender diversity of their STEM program?")
	st.text("% Black vs. sRatio")
	raceSexGraph = alt.Chart(graph_data).mark_circle().encode(
		x='% Black',
		y='sRatio',
		tooltip=['School Name', '% Black', 'sRatio'])

	raceSexGraph + raceSexGraph.transform_regression('% Black', 'sRatio', method="poly").mark_line()

	#st.text("Do socioeconomically disadvantaged schools have less STEM classes?")
	st.text("Free Lunch vs. Courses Offered")
	lunchCourseGraph = alt.Chart(graph_data).mark_circle().encode(
		x='% Free Lunch',
		y='Courses Offered',
		tooltip=['School Name', '% Free Lunch', 'Courses Offered'])

	lunchCourseGraph + lunchCourseGraph.transform_regression('% Free Lunch', 'Courses Offered', method="poly").mark_line()

	#st.text("Do racially diverse schools have less STEM classes, or more?")
	st.text("% Black vs. Courses Offered")
	raceCourseGraph = alt.Chart(graph_data).mark_circle().encode(
		x='% Black',
		y='Courses Offered',
		tooltip=['School Name', '% Black', 'Courses Offered'])

	raceCourseGraph + raceCourseGraph.transform_regression('% Black', 'Courses Offered', method="poly").mark_line()

	#Remove Magnets from graph data to see if they are a source of noise
	graph_data_nm = graph_data.loc[graph_data['Magnet School'] == "No"]

	st.text("% Black vs. Courses Offered (No Magnets)")
	raceCourseGraph_nm = alt.Chart(graph_data_nm).mark_circle().encode(
		x='% Black',
		y='Courses Offered',
		tooltip=['School Name', '% Black', 'Courses Offered'])

	raceCourseGraph_nm + raceCourseGraph_nm.transform_regression('% Black', 'Courses Offered', method="poly").mark_line()

	#st.text("Do larger schools have more or less equal gender representation?")
	st.text("School Size vs. sRatio")
	sizeSexRatio = alt.Chart(graph_data).mark_circle().encode(
		x='Total Students',
		y='sRatio',
		tooltip=['School Name', 'Total Students', 'sRatio'])

	sizeSexRatio + sizeSexRatio.transform_regression('Total Students', 'sRatio', method="linear").mark_line()

	#Output variable correlations
	st.subheader("Correlations")
	correlations = graph_data.corr(method="pearson")
	correlations

	#Crunch math by school type and output
	st.subheader("School Type Analysis")

	#These two are the average by school type with all schools having equal weight.
	#This means a big magnet and small magnet are weighted the same
	st.text(TitleOne(graph_data))
	st.text(Magnet(graph_data))

	#This is a true average of students
	st.text(AllSchools(data))

	st.subheader("Countywide Stats")

	#Enrollment by year
	st.text("Courses taken by year")
	year_data = data["School Year"].value_counts().sort_index()
	year_data

	#Comparison of countywide demographics
	st.text("Countywide, 20.2% percent of students are White,  39.3% are Black, and 3.8% are Asian. 33.7% are ethnically Hispanic.")
	st.text("In STEM, " + calcRace(data, "White") + "% of students are White, " + calcRace(data, "Black") + "% are Black, and " + calcRace(data, "Asian") + "% are Asian. " + calcRace(data, "Hispanic") + "% are ethnically Hispanic.")
	st.text("Black women make up " + calcBlackWomen(data) + "% of STEM Classes")

	st.text("Countywide, the average male student took " + str(calcCRetentionDisp(data)) + " times more STEM courses than the average female student.")

	#Analysis of intro courses
	st.text("")
	st.text("In CS Discoveries and AP Computer Science Principles, two popular introductory courses for students, the sRatio is just " + introCourses(data))
	st.text(introCourseRace(data))
	st.text("Non-intro courses had an average sRatio of " + nonIntroCourses(data))

	#st.text("Mr. Martin's CS Discoveries class is " + martin(data) + "% male.")
