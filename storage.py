#311 Breakdown

zipCode = name_to_zip[zone]
nyc_311_1 = pd.read_csv('https://data.cityofnewyork.us/resource/erm2-nwe9.csv',usecols= ['unique_key','complaint_type','incident_zip'])
print('api to csv')
print(datetime.datetime.now())
nyc_311 = nyc_311_1[nyc_311_1['incident_zip'].isin(zipCode)]
print('csv incident zip filter')
print(datetime.datetime.now())
nyc_311 = nyc_311.groupby(['complaint_type'], sort = True).count()
print('csv complaint type grouping')
print(datetime.datetime.now())
nyc_311 = nyc_311.reset_index()
print('reset index')
print(datetime.datetime.now())
nyc_311.rename(columns= {'complaint_type':'Complaint','unique_key':'Incidents'}, inplace = True)
print('column renaming')
print(datetime.datetime.now())
st.markdown('### 311 Bar Graph')
st.bar_chart(nyc_311, x = 'Complaint', y= 'Incidents', height = 350)
print(datetime.datetime.now())

print(nyc_311_1)


#Trash Collection Numbers

district = name_to_dist[zone]
nyc_refuse = pd.read_csv('https://data.cityofnewyork.us/resource/ebb7-mvp5.csv')
print(datetime.datetime.now())
nyc_refuse = nyc_refuse[nyc_refuse['borough'] == 'Manhattan']
nyc_refuse = nyc_refuse[nyc_refuse['communitydistrict'] == district]
nyc_refuse.rename(columns = {'month':'Month','refusetonscollected':'Refuse','papertonscollected':'Paper','mgptonscollected':'MGP'}, inplace = True)

st.markdown('### Refuse Tonnage')
st.line_chart(nyc_refuse, x = 'Month', y=['Refuse','Paper','MGP'], height = 350)


#Police arrest breakdown

pold = name_to_pd_precint[zone]
nyc_crime = pd.read_csv('https://data.cityofnewyork.us/resource/uip8-fykc.csv')
print(datetime.datetime.now())
nyc_crime = nyc_crime[nyc_crime['arrest_precinct'].isin(pold)]
nyc_crime = nyc_crime.groupby(['pd_desc']).count()
nyc_crime = nyc_crime.reset_index()
nyc_crime.rename(columns = {'pd_desc':'Description','arrest_key':'Incidents'}, inplace = True)

st.markdown('### Recent Crime Breakdown')
st.bar_chart(nyc_crime, x = 'Description', y = 'Incidents', height = 350)



#Traffic collisions

ct = datetime.datetime.now()
nyc_tr_col = pd.read_csv('https://data.cityofnewyork.us/resource/h9gi-nx95.csv?$order=crash_date%20DESC&borough=MANHATTAN')
print(datetime.datetime.now() - ct)
nyc_tr_col = nyc_tr_col[nyc_tr_col['zip_code'].isin(zip)]
nyc_tr_col_amt = nyc_tr_col.groupby(['crash_date']).count()
nyc_tr_col_amt = nyc_tr_col_amt.reset_index()
nyc_tr_col_amt.to_csv('crash_amt.csv')
nyc_tr_col_amt.rename(columns={'crash_date':'Date','borough':'Incidents'}, inplace = True)
nyc_tr_col_fact = nyc_tr_col.groupby(['contributing_factor_vehicle_1']).count()
nyc_tr_col_fact = nyc_tr_col_fact.reset_index()
nyc_tr_col_fact.rename(columns = {'contributing_factor_vehicle_1':'Factor','crash_date':'Instances'},inplace = True)
print(nyc_tr_col)
nyc_tr_col.to_csv('final.csv')
c1, c2, = st.columns((7,3))
with c1:
    st.markdown('### Recent Traffic Accidents')
    st.line_chart(nyc_tr_col_amt, x = 'Date', y = 'Incidents')

with c2:
    st.markdown('### Traffic Accident Factors Breakdown')
    plost.donut_chart(
        data=nyc_tr_col_fact,
        theta='Instances',
        color='Factor',
    ) 

# Hate Crimes

ct = datetime.datetime.now()
nyc_hate_crime = pd.read_csv('https://data.cityofnewyork.us/resource/bqiq-cu78.csv?$order=record_create_date%20DESC&county=NEW%20YORK')
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
