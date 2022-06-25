import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from math import nan

# Config
stem_source = 'prod_data.csv'
DOE_source = 'DOE.csv'

#Math Functions
def calcFreeLunch(row):
	fLunch = row['Free Lunch Eligible'] / row['Total Students']
	return fLunch * 100

def calcPercentBlack(row):
	pBlack = row['Black Students'] / row['Total Students']
	return pBlack * 100

def calcSexRatio(row, data):
	males = ((data['School'] == row['School Name']) & (data['Sex'] == "M")).sum()
	females = ((data['School'] == row['School Name']) & (data['Sex'] == "F")).sum()

	sRatio = round(males/females, 1)

	return sRatio

#Return Number of Title I Schools
def countTitleOne(g_data):
	return len(g_data.loc[g_data['School-wide Title I'] == "Yes"].index)

#Calculate the sRatio average for Title I schools
def calcTitleOneRatio(g_data):
	TitleOneSchools = g_data.loc[g_data['School-wide Title I'] == "Yes"]
	mean = TitleOneSchools['sRatio'].mean()
	return mean

def TitleOne(g_data):
	return "The " + str(countTitleOne(g_data)) + " Title I schools have an average sexRatio of " + str(round(calcTitleOneRatio(g_data), 2))

#Return Number of Title I Schools
def countMagnet(g_data):
	return len(g_data.loc[g_data['Magnet School'] == "Yes"].index)

#Calculate the sRatio average for Title I schools
def calcMagnetRatio(g_data):
	TitleOneSchools = g_data.loc[g_data['Magnet School'] == "Yes"]
	mean = TitleOneSchools['sRatio'].mean()
	return mean

def Magnet(g_data):
	return "The " + str(countMagnet(g_data)) + " magnet schools have an average sexRatio of " + str(round(calcMagnetRatio(g_data), 2))

def AllSchools(data):
	males = (data['Sex'] == "M").sum()
	females = (data['Sex'] == "F").sum()

	sRatio = str(round(males/females, 2))

	return "Countywide, the sexRatio is " + sRatio

def calcRetentionDisp(school, data):
	#Grab all students from school
	students = data.loc[data['School'] == school]

	#Seperate by gender
	m_students = students.loc[students['Sex'] == 'M']
	f_students = students.loc[students['Sex'] == 'F']

	#Catch potential divide by zero
	try:
		m_avg_courses = len(m_students.index) / m_students['Student Number'].nunique()
		f_avg_courses = len(f_students.index) / f_students['Student Number'].nunique()
	except ZeroDivisionError:
	    return "NaN"

	return round(m_avg_courses / f_avg_courses, 2)

#A version of the above function for the entire county
def calcCRetentionDisp(data):
	#Seperate by gender
	m_students = data.loc[data['Sex'] == 'M']
	f_students = data.loc[data['Sex'] == 'F']

	m_avg_courses = len(m_students.index) / m_students['Student Number'].nunique()
	f_avg_courses = len(f_students.index) / f_students['Student Number'].nunique()

	return round(m_avg_courses / f_avg_courses, 2)

def calcRace(data, race):
	#Grab all students of race
	students = data.loc[data['Race Ethnicity'] == race]

	Rcount = len(students.index)
	total = len(data.index)

	return str(round(Rcount / total * 100, 2))

def calcBlackWomen(data):
	#Grab all students of race
	black = data.loc[data['Race Ethnicity'] == "Black"]
	bWomen = black.loc[black['Sex'] == "F"]

	BWcount = len(bWomen.index)
	total = len(data.index)

	return str(round(BWcount / total * 100, 2))


def courseCount(row, data, years):
	name = row['School Name']

	school_students = data.loc[data['School'] == name]

	school_students = school_students.loc[school_students['School Year'] == 2020]

	courseCount = school_students['Course Title'].nunique()

	#If 2020 isn't selected, pick next best year
	if(courseCount == 0):
		bestYear = max(years)

		school_students = data.loc[data['School'] == name]

		school_students = school_students.loc[school_students['School Year'] == int(bestYear)]

		courseCount = school_students['Course Title'].nunique()

	return courseCount

def introCourses(data):
	#Grab students in intro courses
	introStudents = data.loc[
	(data['Course Title'] == "ADVANCED IT HON") |
	(data['Course Title'] == "AP COMP SCI PRIN") |
	(data['Course Title'] == "COMP SCI DISCOVERIES")
	]

	try:
		#Split into male and female students
		maleCount = introStudents['Sex'].value_counts().M
		femaleCount = introStudents['Sex'].value_counts().F

		return str(round(maleCount / femaleCount, 2))
	except:
		pass
		return "Error: NaN"

def nonIntroCourses(data):
	#Grab students in advanced courses
	advStudents = data.loc[
	(data['Course Title'] != "ADVANCED IT HON") &
	(data['Course Title'] != "AP COMP SCI PRIN") &
	(data['Course Title'] != "COMP SCI DISCOVERIES")
	]

	try:
		#Split into male and female students
		maleCount = advStudents['Sex'].value_counts().M
		femaleCount = advStudents['Sex'].value_counts().F

		return str(round(maleCount / femaleCount, 2))
	except:
		pass
		return "Error: NaN"

def martin(data):
	#Grab students in CCHS courses

	introStudents = data.loc[
	(data['Course Title'] == "AP COMP SCI PRIN")
	]

	cciStudents = introStudents.loc[
	(introStudents['School'] == "COOPER CITY HIGH")
	]
	try:
		#Split into male and female students
		maleCount = cciStudents['Sex'].value_counts().M
		femaleCount = cciStudents['Sex'].value_counts().F

		return str(round(((maleCount / femaleCount) / ((maleCount / femaleCount) + 1) * 100), 2))
	except:
		pass
		return "Error: NaN"


def introCourseRace(data):
	#Grab students in intro courses
	introStudents = data.loc[
	(data['Course Title'] == "ADVANCED IT HON") |
	(data['Course Title'] == "AP COMP SCI PRIN") |
	(data['Course Title'] == "COMP SCI DISCOVERIES")
	]

	#Grab all students of race
	Wstudents = introStudents.loc[introStudents['Race Ethnicity'] == "White"]
	Bstudents = introStudents.loc[introStudents['Race Ethnicity'] == "Black"]
	Astudents = introStudents.loc[introStudents['Race Ethnicity'] == "Asian"]

	#Count them
	Wcount = len(Wstudents.index)
	Bcount = len(Bstudents.index)
	Acount = len(Astudents.index)

	#Get Total
	total = len(introStudents.index)

	if(total != 0):
		WPercent = str(round(Wcount / total * 100, 2))
		BPercent = str(round(Bcount / total * 100, 2))
		APercent = str(round(Acount / total * 100, 2))

		return "In the same intro courses, " + WPercent + "% of students are White, " + BPercent + "% are Black, and " + APercent + "% are Asian."

	else:
		return "No students were enrolled in intro courses in the selected years, so a demographic breakdown isn't available."

def yearFilter(data, years, yearList):
	#Make empty data frame
	filtered = pd.DataFrame(columns=data.columns)

	#If for each year, if it was selected, add to data for analysis
	for year in yearList:
		if year in years:
			yearData = data.loc[(data['School Year'] == int(year))]
			filtered = filtered.append(yearData, ignore_index=True)

	return filtered

def t1Filter(data, DOE, titleOneMode):
	if(titleOneMode == 'Title I Schools'):
		#Grab T1 Schools
		t1Schools = []

		t1Only = DOE.loc[(DOE['School-wide Title I'] == "Yes")]

		for index, row in t1Only.iterrows():
			t1Schools.append(row["School Name"])

		return data[data['School'].isin(t1Schools)]

	elif(titleOneMode == 'Non Title I'):
		#Grab T1 Schools
		nTSchools = []

		nTOnly = DOE.loc[(DOE['School-wide Title I'] == "No")]

		for index, row in nTOnly.iterrows():
			nTSchools.append(row["School Name"])

		return data[data['School'].isin(nTSchools)]
	else:
		return data

#Loading Functions
@st.cache
def loadSTEMData():
	data = pd.read_csv(stem_source)
	return data

@st.cache
def loadDOEData():
	data = pd.read_csv(DOE_source)
	return data

@st.cache
def loadGraphData(main, DOE, years):
	#Start with DOE data
	g_data = DOE.copy()

	#Calculate percents
	g_data['% Free Lunch'] = g_data.apply(lambda row: calcFreeLunch(row), axis=1)
	g_data['% Black'] = g_data.apply(lambda row: calcPercentBlack(row), axis=1)
	g_data['Courses Offered'] = g_data.apply(lambda row: courseCount(row, main, years), axis=1)

	#Calculate Sex Ratio
	g_data['sRatio'] = g_data.apply(lambda row: calcSexRatio(row, main), axis=1)

	sexTotal = main.groupby(["School"])["Sex"].count().reset_index()

	#Discard unneeded data for organization purposes
	g_data.drop('Free Lunch Eligible', axis=1, inplace=True)
	g_data.drop('Hispanic Students', axis=1, inplace=True)
	g_data.drop('Black Students', axis=1, inplace=True)
	g_data.drop('White Students', axis=1, inplace=True)
	g_data.drop('Two or More Races Students', axis=1, inplace=True)

	return g_data
