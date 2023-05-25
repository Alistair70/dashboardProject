# Testing area for sub-sections of the overall project

import streamlit as st
import pandas as pd
import plost
import plotly.graph_objects as go

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

zipAll = [10025,10031,10039,10026,10027,10030,10037,10029,10035,10032,10033,10040]

name_to_pd_precint = {'West Harlem' : [24,26,30],
                      'Central Harlem' : [28,32],
                      'East Harlem' : [23,25],
                      'Washinton Heights' : [33,34]}

zone = 'Central Harlem'
zip = name_to_zip[zone]
pol_pd = name_to_pd_precint[zone]
pold = name_to_pd_precint[zone]
zipCode = name_to_zip[zone]

@st.cache_data(ttl=1800)
def getData():
    data = pd.read_csv('https://data.cityofnewyork.us/resource/ebb7-mvp5.csv')
    return data


district = name_to_dist[zone]
nyc_refuse = getData()
nyc_refuse = nyc_refuse[nyc_refuse['borough'] == 'Manhattan']
nyc_refuse = nyc_refuse[nyc_refuse['communitydistrict'] == district]
nyc_refuse.rename(columns = {'month':'Month','refusetonscollected':'Refuse','papertonscollected':'Paper','mgptonscollected':'MGP'}, inplace = True)

sorted = nyc_refuse.sort_values('Month')

trace1 = go.Scatter(x = sorted['Month'], y = sorted['Refuse'], mode = 'lines', name = 'Refuse')
trace2 = go.Scatter(x = sorted['Month'], y = sorted['Paper'], mode  = 'lines', name = 'Paper')
trace3 = go.Scatter(x = sorted['Month'], y = sorted['MGP'], mode  = 'lines', name = 'Metal/Glass/Plastic')

layout = go.Layout(title='Sample Line Chart', xaxis=dict(title='X-axis'), yaxis=dict(title='Y-axis'), autosize=True)

fig = go.Figure(data = [trace1,trace2,trace3], layout = layout)
st.plotly_chart(fig, use_container_width=True)

st.markdown('### Refuse Tonnage')
st.line_chart(nyc_refuse, x = 'Month', y=['Refuse','Paper','MGP'], height = 350, width=350)

