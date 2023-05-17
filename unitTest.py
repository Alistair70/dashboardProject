# Testing area for sub-sections of the overall project

import streamlit as st
import pandas as pd
import plost
import datetime

st.set_page_config(layout='wide', initial_sidebar_state='expanded')

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


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

print(datetime.datetime.now())
zone = 'Central Harlem'
zip = name_to_zip[zone]
pol_pd = name_to_pd_precint[zone]

ct = datetime.datetime.now()
nyc_hate_crime = pd.read_csv('https://data.cityofnewyork.us/resource/bqiq-cu78.csv?$order=record_create_date%20DESC')
print(datetime.datetime.now() - ct)
nyc_hate_crime = nyc_hate_crime[nyc_hate_crime['complaint_precinct_code'].isin(pol_pd)]
nyc_hate_crime.to_csv('hate_crimes.csv')

nyc_hate_crime_bias = nyc_hate_crime.groupby(['bias_motive_description']).count()
nyc_hate_crime_bias = nyc_hate_crime_bias.reset_index()
nyc_hate_crime_bias.rename(columns={'bias_motive_description':'Bias','full_complaint_id':'Instances'},inplace = True)


nyc_hate_crime_offense = nyc_hate_crime.groupby(['offense_category']).count()
nyc_hate_crime_offense = nyc_hate_crime_offense.reset_index()
nyc_hate_crime_offense.rename(columns = {'offense_category':'Offense','full_complaint_id':'Instances'},inplace = True)
nyc_hate_crime_offense.to_csv('offense.csv')

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

#nyc .rename(columns = {'pd_desc':'Description','arrest_key':'Incidents'}, inplace = True)
