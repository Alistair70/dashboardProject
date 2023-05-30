import streamlit as st
import pandas as pd
import plost
from streamlit_autorefresh import st_autorefresh

secs = 1 * 1000

st.set_page_config(layout='wide')
st_autorefresh(interval=10000)      # Number represents time units. Units here in milliseconds

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

hide = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
        """
st.markdown(hide, unsafe_allow_html=True)

st.header('Uptown Community Dashboard')

# Creates a dropdown options box for each of the four districts - May change names in future
st.subheader('District')
zone = st.selectbox('Select District',('West Harlem','Central Harlem','East Harlem','Washinton Heights'))

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

# Getting and Caching Data
@st.cache_data(ttl=11)      # Number represents time units. Units here in seconds
def getRefuseData():
    data = pd.read_csv('https://data.cityofnewyork.us/resource/ebb7-mvp5.csv')
    return data
def get311Data():
    data = pd.read_csv('https://data.cityofnewyork.us/resource/sebv-z45x.csv')
    return data
def getCrimeData():
    data = pd.read_csv('https://data.cityofnewyork.us/resource/uip8-fykc.csv')
    return data
def getTrafficAccData():
    data = pd.read_csv('https://data.cityofnewyork.us/resource/h9gi-nx95.csv?$order=crash_date%20DESC&borough=MANHATTAN', 
                         usecols={'zip_code','crash_date','borough','contributing_factor_vehicle_1'})
    return data
def getHateCrimeData():
    data = pd.read_csv('https://data.cityofnewyork.us/resource/bqiq-cu78.csv?$order=record_create_date%20DESC&$limit=2200')
    return data


########## Logic

# Logic 1 - Crime
pol_pd = name_to_pd_precint[zone]
nyc_crime = getCrimeData()
nyc_crime = nyc_crime[nyc_crime['arrest_precinct'].isin(pol_pd)]
nyc_crime = nyc_crime.groupby(['ofns_desc']).count()
nyc_crime = nyc_crime.reset_index()
nyc_crime.rename(columns = {'ofns_desc':'Description','arrest_key':'Incidents'}, inplace = True)

# Logic 2 - 311 breakdown
zipCode = name_to_zip[zone]
nyc_311 = get311Data()
nyc_311 = nyc_311[nyc_311['Incident Zip'].isin(zipCode)]
nyc_311 = nyc_311.groupby(['Complaint Type'], sort = True).count()
nyc_311 = nyc_311.reset_index() 
nyc_311.rename(columns= {'Complaint Type':'Complaint','Unique Key':'Incidents'}, inplace = True)
nyc_311 = nyc_311.sort_values(by=['Incidents'], ascending=False)

noise = ['Noise - Residential','Noise - Street/Sidewalk','Noise','Noise - Commercial','Noise - Vehicle','Noise - Helicopter','Noise - Park','Noise - House of Worship']
util_comp = ['HEAT/HOT WATER','PLUMBING','ELECTRIC','WATER LEAK']
housing_comp = ['PAINT/PLASTER','DOOR/WINDOW','FLOORING/STAIRS','ELEVATOR']

Complaint = ['Noise','Illegal Parking','Unsanitory Condition','Utility Issues','Non-Emergency Police','Rodent','Housing Complaint','Other']
Amount = [0,0,0,0,0,0,0,0]

for i in nyc_311.index:
    if nyc_311['Complaint'][i] in noise:
        Amount[0] += nyc_311['Incidents'][i]
    elif 'Illegal Parking' in nyc_311['Complaint'][i]:
        Amount[1] += nyc_311['Incidents'][i]
    elif 'UNSANITARY CONDITION' in nyc_311['Complaint'][i]:
        Amount[2] += nyc_311['Incidents'][i]
    elif nyc_311['Complaint'][i] in util_comp:
        Amount[3] += nyc_311['Incidents'][i]
    elif 'Non-Emergency Police' in nyc_311['Complaint'][i]:
        Amount[4] += nyc_311['Incidents'][i]
    elif 'Rodent' in nyc_311['Complaint'][i]:
        Amount[5] += nyc_311['Incidents'][i]
    elif nyc_311['Complaint'][i] in housing_comp:
        Amount[6] += nyc_311['Incidents'][i]
    else:
        Amount[7] += nyc_311['Incident Zip'][i]

data = {'Complaint': Complaint, 'Incidents':Amount}
df = pd.DataFrame.from_dict(data)


#Logic 3 - Traffic Accidents
zip = name_to_zip[zone]
nyc_tr_col = getTrafficAccData()
nyc_tr_col = nyc_tr_col[nyc_tr_col['zip_code'].isin(zip)]

#Logic 3a - Amount of Traffic Accidents
nyc_tr_col_amt = nyc_tr_col.groupby(['crash_date']).count()
nyc_tr_col_amt = nyc_tr_col_amt.reset_index()
nyc_tr_col_amt.rename(columns={'crash_date':'Date','borough':'Incidents'}, inplace = True)
nyc_tr_col_amt['Date'] = pd.to_datetime(nyc_tr_col_amt['Date'])

s = nyc_tr_col_amt['Date'].iloc[0]
e = nyc_tr_col_amt['Date'].iloc[-1] 

missing_dates = pd.date_range(start = s, end = e).difference(nyc_tr_col_amt['Date'])

for i in missing_dates:
    nyc_tr_col_amt.loc[len(nyc_tr_col_amt.index)] = [i, 0, 0, 0] 

nyc_tr_col_amt = nyc_tr_col_amt.sort_values(by=['Date'])

#Logic 3b - Factors behind Traffic Accidents
nyc_tr_col_fact = nyc_tr_col.groupby(['contributing_factor_vehicle_1']).count()
nyc_tr_col_fact = nyc_tr_col_fact.reset_index()
nyc_tr_col_fact.rename(columns = {'contributing_factor_vehicle_1':'Factor','crash_date':'Instances'},inplace = True)
nyc_tr_col_fact = nyc_tr_col_fact.sort_values(by='Instances', ascending=False)

f1 = nyc_tr_col_fact['Factor'].values.tolist()
i1 = nyc_tr_col_fact['Instances'].values.tolist()

remove = len(i1) - 9
total_other = sum(i1[-remove:])

f1 = f1[: len(f1) - remove]
i1 = i1[: len(i1) - remove]

f1.append('Other')
i1.append(total_other)

factors = {'Factor':f1,'Instances':i1}
factors_df = pd.DataFrame(factors)

#Logic 4
nyc_hate_crime = getHateCrimeData()
#nyc_hate_crime = nyc_hate_crime[nyc_hate_crime['complaint_precinct_code'].isin(pol_pd)]

# Logic 4a - Hate Crime Bias
nyc_hate_crime_bias = nyc_hate_crime.groupby(['bias_motive_description']).count()
nyc_hate_crime_bias = nyc_hate_crime_bias.reset_index()
nyc_hate_crime_bias.rename(columns={'bias_motive_description':'Bias','full_complaint_id':'Instances'},inplace = True)

# Login 4b - Hate Crime Offenses
nyc_hate_crime_offense = nyc_hate_crime.groupby(['offense_category']).count()
nyc_hate_crime_offense = nyc_hate_crime_offense.reset_index()
nyc_hate_crime_offense.rename(columns = {'offense_category':'Offense','full_complaint_id':'Instances'},inplace = True)

# Logic 5 - Refuse Line Graph
district = name_to_dist[zone]
nyc_refuse = getRefuseData()
nyc_refuse = nyc_refuse[nyc_refuse['borough'] == 'Manhattan']
nyc_refuse = nyc_refuse[nyc_refuse['communitydistrict'] == district]
nyc_refuse.rename(columns = {'month':'Month','refusetonscollected':'Refuse','papertonscollected':'Paper','mgptonscollected':'MGP'}, inplace = True)

########## Graphics

#Row 1 - Crime Breakdown 
st.markdown('### Recent Crime Breakdown')
st.bar_chart(nyc_crime, x = 'Description', y = 'Incidents', height = 500)

#Row 2 - 311 Bar Graph
st.markdown('### 311 Bar Graph')
st.bar_chart(data, x = 'Complaint', y= 'Incidents', height = 350)

#Row 3 - Traffic Accidents
c1, c2, = st.columns((7,3))
with c1:
    st.markdown('### Recent Traffic Accidents')
    st.line_chart(nyc_tr_col_amt, x = 'Date', y = 'Incidents', height = 350)

with c2:
    st.markdown('### Traffic Accident Factors')
    plost.donut_chart(
        data=factors_df,
        theta='Instances',
        color='Factor',
        legend='bottom', 
        use_container_width=True)  

# Row 4 - Hate Crimes - City-Wide
c1, c2, = st.columns((7,3))
with c1:
    st.markdown('### City-Wide Hate Crime Biases')
    st.bar_chart(nyc_hate_crime_bias, x = 'Bias', y = 'Instances', height = 500)
with c2:
    st.markdown('### City-Wide Hate Crime Offences')
    plost.donut_chart(
        data=nyc_hate_crime_offense,
        theta='Instances',
        color='Offense',
        legend='bottom', 
        use_container_width=True)
    
#Row 1 - Refuse/Paper/MGP Tonnage
st.markdown('### Refuse Tonnage')
st.line_chart(nyc_refuse, x = 'Month', y=['Refuse','Paper','MGP'], height = 350 )