import streamlit as st
import pandas as pd
import plost
import datetime

st.set_page_config(layout='wide', initial_sidebar_state='expanded')

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    
st.sidebar.header('Dashboard `version 3`')

# Creates a dropdown options box for each of the four districts - May change names in future

st.sidebar.subheader('District')
zone = st.sidebar.selectbox('Select District',('West Harlem','Central Harlem','East Harlem','Washinton Heights'))

st.sidebar.subheader('Select Borough')
time_hist_color = st.sidebar.selectbox('Color by', ('temp_min', 'temp_max')) 

st.sidebar.subheader('Donut chart parameter')
donut_theta = st.sidebar.selectbox('Select data', ('q2', 'q3'))

st.sidebar.subheader('Line chart parameters')
plot_data = st.sidebar.multiselect('Select data', ['temp_min', 'temp_max'], ['temp_min', 'temp_max'])
plot_height = st.sidebar.slider('Specify plot height', 200, 500, 250)



st.sidebar.markdown('''
---
Created with ❤️ by [Data Professor](https://youtube.com/dataprofessor/).
''')

# Relating District Names with zip codes and community/districs numbers

name_to_dist = {'West Harlem':'09',
                'Central Harlem':'10',
                'East Harlem':'11',
                'Washinton Heights':'12'}

name_to_zip = {'West Harlem':[10025,10031,10039],
               'Central Harlem':[10026,10027,10030,10037],
               'East Harlem' : [10029,10035],
               'Washinton Heights' : [10032,10033,10040]}

name_to_pd_precint = {'West Harlem' : [24,26,30],
                      'Central Harlem' : [28,32],
                      'East Harlem' : [23,25],
                      'Washinton Heights' : [33,34]}

########## Logic

# Logic 1 - Refuse Line Graph

district = name_to_dist[zone]
ct = datetime.datetime.now()
nyc_refuse = pd.read_csv('https://data.cityofnewyork.us/resource/ebb7-mvp5.csv')
print(datetime.datetime.now() - ct)
nyc_refuse = nyc_refuse[nyc_refuse['borough'] == 'Manhattan']
nyc_refuse = nyc_refuse[nyc_refuse['communitydistrict'] == district]
nyc_refuse.rename(columns = {'month':'Month','refusetonscollected':'Refuse','papertonscollected':'Paper','mgptonscollected':'MGP'}, inplace = True)

# Logic 2 - 311 breakdown

zipCode = name_to_zip[zone]
ct = datetime.datetime.now()
nyc_311 = pd.read_csv('https://data.cityofnewyork.us/resource/sebv-z45x.csv')
print(datetime.datetime.now() - ct)
nyc_311 = nyc_311[nyc_311['Incident Zip'].isin(zipCode)]
nyc_311 = nyc_311.groupby(['Complaint Type'], sort = True).count()
nyc_311 = nyc_311.reset_index()
nyc_311.rename(columns= {'Complaint Type':'Complaint','Unique Key':'Incidents'}, inplace = True)

# Logic 3 - Crime

pol_pd = name_to_pd_precint[zone]
ct = datetime.datetime.now()
nyc_crime = pd.read_csv('https://data.cityofnewyork.us/resource/uip8-fykc.csv')
print(datetime.datetime.now() - ct)
nyc_crime = nyc_crime[nyc_crime['arrest_precinct'].isin(pol_pd)]
nyc_crime = nyc_crime.groupby(['pd_desc']).count()
nyc_crime = nyc_crime.reset_index()
nyc_crime.rename(columns = {'pd_desc':'Description','arrest_key':'Incidents'}, inplace = True)

#Logic 4 - Traffic Accidents

zip = name_to_zip[zone]
ct = datetime.datetime.now()
nyc_tr_col = pd.read_csv('https://data.cityofnewyork.us/resource/h9gi-nx95.csv?$order=crash_date%20DESC&borough=MANHATTAN')
print(datetime.datetime.now() - ct)
nyc_tr_col = nyc_tr_col[nyc_tr_col['zip_code'].isin(zip)]

#Logic 4a - Amount of Traffic Accidents

nyc_tr_col_amt = nyc_tr_col.groupby(['crash_date']).count()
nyc_tr_col_amt = nyc_tr_col_amt.reset_index()
nyc_tr_col_amt.to_csv('crash_amt.csv')
nyc_tr_col_amt.rename(columns={'crash_date':'Date','borough':'Incidents'}, inplace = True)

#Logic 4b - Factors behind Traffic Accidents

nyc_tr_col_fact = nyc_tr_col.groupby(['contributing_factor_vehicle_1']).count()
nyc_tr_col_fact = nyc_tr_col_fact.reset_index()
nyc_tr_col_fact.rename(columns = {'contributing_factor_vehicle_1':'Factor','crash_date':'Instances'},inplace = True)

#Logic 5

ct = datetime.datetime.now()
nyc_hate_crime = pd.read_csv('https://data.cityofnewyork.us/resource/bqiq-cu78.csv?$order=record_create_date%20DESC&$limit=2200')
print(datetime.datetime.now() - ct)
#nyc_hate_crime = nyc_hate_crime[nyc_hate_crime['complaint_precinct_code'].isin(pol_pd)]
nyc_hate_crime.to_csv('hate_crimes.csv')

# Logic 5a - Hate Crime Bias

nyc_hate_crime_bias = nyc_hate_crime.groupby(['bias_motive_description']).count()
nyc_hate_crime_bias = nyc_hate_crime_bias.reset_index()
nyc_hate_crime_bias.rename(columns={'bias_motive_description':'Bias','full_complaint_id':'Instances'},inplace = True)

# Login 5b - Hate Crime Offenses

nyc_hate_crime_offense = nyc_hate_crime.groupby(['offense_category']).count()
nyc_hate_crime_offense = nyc_hate_crime_offense.reset_index()
nyc_hate_crime_offense.rename(columns = {'offense_category':'Offense','full_complaint_id':'Instances'},inplace = True)

########## Graphics

#Row 1 - Refuse/Paper/MGP Tonnage

st.markdown('### Refuse Tonnage')
st.line_chart(nyc_refuse, x = 'Month', y=['Refuse','Paper','MGP'], height=plot_height )

#Row 2 - 311 Bar Graph

st.markdown('### 311 Bar Graph')
st.bar_chart(nyc_311, x = 'Complaint', y= 'Incidents', height = 350)

#Row 3 - Crime Breakdown 
st.markdown('### Recent Crime Breakdown')
st.bar_chart(nyc_crime, x = 'Description', y = 'Incidents', height = 350)

#Row 4 - Traffic Accidents
c1, c2, = st.columns((7,3))
with c1:
    st.markdown('### Recent Traffic Accidents')
    st.line_chart(nyc_tr_col_amt, x = 'Date', y = 'Incidents')

with c2:
    st.markdown('### Traffic Accident Factors')
    plost.donut_chart(
        data=nyc_tr_col_fact,
        theta='Instances',
        color='Factor',
        legend='bottom', 
        use_container_width=True)  

# Row 5 - Hate Crimes - to-do Change to all New york

c1, c2, = st.columns((7,3))
with c1:
    st.markdown('### Hate Crime Biases')
    st.bar_chart(nyc_hate_crime_bias, x = 'Bias', y = 'Instances', height = 350)
with c2:
    st.markdown('### Hate Crime Offences')
    plost.donut_chart(
        data=nyc_hate_crime_offense,
        theta='Instances',
        color='Offense',
        legend='bottom', 
        use_container_width=True)

# Row A
st.markdown('### Metrics')
col1, col2, col3 = st.columns(3)
col1.metric("Temperature", "70 °F", "1.2 °F")
col2.metric("Wind", "9 mph", "-8%")
col3.metric("Humidity", "86%", "4%")