import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from numerize import numerize
import plotly.express as px
import plotly.graph_objects as go
import datetime as dt
import streamlit as st
import re


st.set_page_config(layout='wide')
#common variable
years = list(range(2015,2020))

def clean_dataset(df):
    # st.write(df.columns.tolist())
    df.drop(columns= ['Remarks','Sr No'],axis=1 , inplace=True)
    df.dropna(subset=['InvestmentnType','Investors Name'],inplace=True)
    df.rename(mapper={
        'Date dd/mm/yyyy':'Startup_date',
        'City  Location':'City',
        'Amount in USD':'Amount',
        'Startup Name':'Startupname',
        'Industry Vertical':'Industrytype',
        'Investors Name':'Investorsname'
        },axis=1, inplace=True)
    df['City'].replace(np.NaN,df['City'].value_counts().idxmax(),inplace= True)
    df['Industrytype'].replace(np.NaN,df['Industrytype'].value_counts().idxmax(),inplace=True)
    df['SubVertical'].replace(np.nan, df['SubVertical'].value_counts().idxmax(), inplace=True)
    df['Amount'] = df['Amount'].apply(clean_amount)
    df["Amount"] = df["Amount"].astype(float)

    return df

def make_money_readable(amount):
    return numerize.numerize(amount)
    return amount

def clean_date_str(date_str):
    try:
        out = re.match(r'\d\d/\d\d/\d\d\d\d',date_str)
        if out:
            return date_str
        else:
            return np.nan
    except:
        return np.nan
  
    
def clean_amount(amt):
    amt = str(amt)
    if ',' in amt:
        amt = amt.replace(',','')
    if amt.isnumeric():
        return float(amt)
    if amt.isalpha() or amt.startswith('\\'):
        return np.nan
    if '.' in amt:
        return float(amt)
    if '+' in amt:
        return float(amt.replace('+',''))
    return np.nan


st.cache()                                                       
def load_dataset():
    df = pd.read_csv('data/startup_funding.csv')
    df = clean_dataset(df)
    df['Startup_date'] = df.Startup_date.apply(clean_date_str)
    df['Startup_date'] = pd.to_datetime(df['Startup_date'])
    df['Year'] = df['Startup_date'].dt.year
    #df['Clean_date'].replace(np.NaN,df['Clean_date'].value_counts().idxmax(),inplace=True)    
    return df

st.title("Startups in India  from 2015-2020")
with st.spinner("loading dataset"):                               
    df= load_dataset()


if st.sidebar.checkbox("View KPI for startup in India"):

    st.subheader("Startup Investment summary")
    col1,col2,col3 = st.columns(3)
    col1.metric("Maximum Amount(Rapido Taxi)", "$3900000000", "2019-08-27")
    col2.metric("Amount Mean", "$18292675.43")
    col3.metric("Minimum Amount (Hostel Dunia)", "$16000", "2015-01-19")
    st.subheader('Year wise startup summary')
    cal1,cal2,cal3 = st.columns(3)
    cal1.metric("Maximum Startups in year","2016"," 992","inverse")
    cal2.metric("Average Startups per year",604)
    cal3.metric(label="Minimum Startups in year", value=2020, delta=-7,delta_color="off")
    st.subheader("Startups city wise summary")
    nam1, nam2, _= st.columns(3)
    nam1.metric("Maximum Startups in  a city","Bangalore", 879,)
    nam2.metric("Minimum Startups in  a city", "Bhubneswar", -1)

if st.sidebar.checkbox('show full dataframe'):                 
    st.write(df,use_container_width=True)
    row,col = df.shape

years = df.Startup_date.dt.year.unique().tolist()
yr = st.sidebar.selectbox("Years",years)


cities = df.City.unique().tolist()
city= st.sidebar.selectbox("City",cities)

#g1
years= df.groupby(df.Startup_date.dt.year)['Industrytype'].count().reset_index()
years.columns = ['years','Industry']
fig1= px.bar(years,'years','Industry',title='Sector covers most number of startup with years')
# add a line chart
fig1.add_trace(go.Scatter(x=years['years'], y=years['Industry'], mode='lines', name='lines'))
st.plotly_chart(fig1, use_container_width=True)
st.info('''Conclusion: The above graph shows the number of startups in each year, the line chart shows the trend of startups in each year, 
        2016 has the highest number of startups and 2020 has the lowest number of startups.''')

fig2 = px.box(df[df['Startup_date'].dt.year == yr], 'City', 'Amount', hover_name='Startupname', height=600)
st.plotly_chart(fig2, use_container_width=True)

# city wise graph for year 

#st.sidebar.write(df.dtypes)
citydf = df[df['City'] == city].copy()
citydf.sort_values(by='Year', inplace=True)
try:
    fig3 = px.treemap(
    citydf,
    path=['Year', 'Startupname', 'Industrytype'],
    values='Amount',
    color='Amount',
    color_continuous_scale='RdBu',
    height=600)
    st.plotly_chart(fig3, use_container_width=True)
except:
    st.error('No data available')


#graph startupname and industry type wise
#st.sidebar.write(df.dtypes)
citydf = df[df['City'] == city].copy()  
citydf.sort_values(by='Startupname', inplace=True)
fig4 = px.scatter(citydf, x='Startupname', y='Industrytype', color='Amount', title='Startupname and Industrytype', height=600)
st.plotly_chart(fig4, use_container_width=True)


#graph for city and industry type wise
#st.sidebar.write(df.dtypes) 
citydf = df[df['City'] == city].copy()
citydf.sort_values(by='City', inplace=True) 
fig5= px.pie(citydf, values='Amount', names='Industrytype', title='Industry type wise investment in city', height=650)
st.plotly_chart(fig5, use_container_width=True)

#multiple line chart
#st.sidebar.write(df.dtypes) 
citydf = df[df['City'] == city].copy()
citydf.sort_values(by='City', inplace=True) 
fig6= px.scatter_3d(citydf, x='Startupname', y='Industrytype', z='Amount', color='Startupname', title='Startupname, Industrytype and Amount', height=800)
st.plotly_chart(fig6, use_container_width=True)

#graph on scatter matrix
#st.sidebar.write(df.dtypes) 
citydf = df[df['City'] == city].copy()
citydf.sort_values(by='City', inplace=True)
fig7= px.scatter_matrix(citydf, dimensions=['Startupname', 'Industrytype', 'Year'], color='Startupname', title='Startupname, Industrytype and Years', height=800)    
st.plotly_chart(fig7, use_container_width=True)