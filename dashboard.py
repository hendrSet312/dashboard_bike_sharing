import pandas as pd
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt 
import seaborn as sns

plt.rc('font', size=15)

def get_color(ser):
    max_index = ser[ser == ser.max()].index
    return ['#FF7F0E' if x == max_index else '#AE9166' for x in ser.index]

#get grouped sum value based on any column
def grouped_columns(df,groupby_column,column_target):
    grouped_column = df.groupby(groupby_column).sum(numeric_only = True)[column_target]
    return grouped_column.sort_values(ascending = False)

#get the sum of casual and registered user
def prop_user(df):
    return df[['casual','registered']].sum()

#get the transformation for heatmap
def transform_heatmap(df,column_traget):
    heatmap_data = df.pivot_table(index='month', columns='weekday', values=column_traget, aggfunc='sum') / 10000
    return heatmap_data


#cleaning the data
def cleaning_data(df):
    weekday_dict = {
        0:'Sunday',
        1:'Monday',
        2:'Tuesday',
        3:'Wednesday',
        4:'Thursday',
        5:'Friday',
        6:'Saturday'
    }

    month_dict = {
        1: 'Jan',
        2: 'Feb',
        3: 'Mar',
        4: 'Apr',
        5: 'May',
        6: 'Jun',
        7: 'Jul',
        8: 'Aug',
        9: 'Sep',
        10: 'Oct',
        11: 'Nov',
        12: 'Dec'
    }

    weather_dict = {
        1:'Clear',
        2:'Mist/cloudy',
        3:'Light snow/rain',
        4:'Heavy snow/Rain'
    }

    season_dict = {1:'springer', 2:'summer', 3:'fall', 4:'winter'}

    #change the value of the date
    df['yr'] = df['yr'].apply(lambda x : 2011 if x == 0 else 2012)
    df['mnth'] = df['mnth'].map(month_dict)
    df['weekday'] = df['weekday'].map(weekday_dict)
    df['season'] = df['season'].map(season_dict)
    df['weathersit'] = df['weathersit'].map(weather_dict)
    df['holiday'] = df['holiday'].apply(lambda x : 'Yes' if x == 1 else 'False')

    #unnormalize the data
    df['temp'] = df['temp'] * 40
    df['atemp'] = df['atemp'] * 50 
    df['hum'] = df['hum'] * 100
    df['windspeed'] = df['windspeed'] * 67

    #rename the column 
    df = df.rename(columns = {'mnth':'month','yr':'year','cnt':'total'})

    return df.drop(columns = ['instant'])

#import data
df = pd.read_csv("day.csv",parse_dates=['dteday'])
df.sort_values(by = 'dteday',inplace=True)

#get minimum and maximum value
min_date = df['dteday'].min()
max_date = df['dteday'].max()

st.header("🚴 Bicycle Rent Dashboard 🚴")
st.write(
    """
        Bike sharing systems are new generation of traditional bike rentals where whole process from membership, rental and return 
back has become automatic. Through these systems, user is able to easily rent a bike from a particular position and return 
back at another position. Currently, there are about over 500 bike-sharing programs around the world which is composed of 
over 500 thousands bicycles. Today, there exists great interest in these systems due to their important role in traffic, 
environmental and health issues. 
    """
)

#date range side bar
with st.sidebar:
    st.header("Choose a Date Range")
    start_date, end_date = st.date_input(
        label='Date Range',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

#filtering data
df = df[(df['dteday'] >= str(min_date)) & (df['dteday'] <= str(max_date))]
df = cleaning_data(df)

#generate proportion of user
prop_df = prop_user(df)

#generate rent statistics 
col1, col2, col3= st.columns(3)
 
with col1:
    total_rent = df['total'].sum()
    st.metric("Total rent :", value=total_rent)

with col2:
    avg_rent = round(df['total'].mean(),0)
    st.metric("Avg. rent/day :", value=avg_rent)

with col3:
    highest_rent = round(df['total'].max(),0)
    st.metric("Highest. rent count:", value = highest_rent)

#generate rent linechart
with st.container():

    st.subheader('🗓️ Daily Rent')

    list_user = ['casual','registered','total']
    list_color = ['#DF2935','#FDCA40','#3772FF']

    selected_user = st.multiselect("Select User", list_user)

    selected_color = [list_color[x] for x in range(len(selected_user))]

    df_selected = df[selected_user+['dteday']].set_index('dteday')

    st.line_chart(df_selected,color = selected_color)


#user proportion and weather situation proportion
with st.container():
    col6,col7= st.columns(2)
    with col6: 
        st.subheader('👤 User Proportion')
        fig,axes = plt.subplots(1,figsize = (6,6))
        prop_df.plot(kind = 'pie',autopct = '%.2f%%',ax = axes)
        
        st.pyplot(fig)

    with col7 :
        fig,axes = plt.subplots(1,figsize = (6,6))
        st.subheader('🌦️ Weather Situation')

        weather_counts = df['weathersit'].value_counts()
        colors = get_color(weather_counts)

        countweather = weather_counts.plot(kind = 'bar',color = colors)
        countweather.set_xticklabels(countweather.get_xticklabels(), rotation=30)
        st.pyplot(fig)

#detail info of user
st.subheader('🔍 User Detailed Info')

#make tabs for casual and registered user 
tab1, tab2 = st.tabs(["Casual", "Registered"])

with tab1 : 
    st.subheader("Casual User")
    
    #statistics for casual user
    with st.container():
        col_casual1, col_casual2 = st.columns(2)
        with col_casual1:
            total_rent = df['casual'].sum()
            st.metric("Total:", value=total_rent)

        with col_casual2:
            avg_rent = round(df['casual'].mean(),0)
            st.metric("Avg. rent:", value=avg_rent)
    
    #casual user intensity
    st.subheader("Casual User Intensity")
    st.write('*The number is normalized by divide it with 10000')

    df_transform = transform_heatmap(df,'casual')

    fig,axes = plt.subplots(figsize = (16,10))

    sns.heatmap(df_transform, axes = axes,annot = True)

    st.pyplot(fig)

    #casual user highest value by month, days and year
    with st.container():
        st.subheader("Month")
        fig,axes = plt.subplots(figsize = (10,6))
        grouped = grouped_columns(df,'month','casual')
        colors = get_color(grouped)
        plot_image = grouped.plot(kind = 'bar',color = colors,axes = axes)
        plot_image.set_xticklabels(plot_image.get_xticklabels(), rotation=30)
        st.pyplot(fig)

    with st.container():
        st.subheader("Weekday")
        fig,axes = plt.subplots(figsize = (10,6))
        grouped = grouped_columns(df,'weekday','casual')
        colors = get_color(grouped)
        plot_image = grouped.plot(kind = 'bar',color = colors,axes = axes)
        plot_image.set_xticklabels(plot_image.get_xticklabels(), rotation=30)
        st.pyplot(fig)

    with st.container():
        st.subheader("Year")
        fig,axes = plt.subplots(figsize = (10,6))
        grouped = grouped_columns(df,'year','casual')
        colors = get_color(grouped)
        grouped.plot(kind = 'barh',color = colors,axes = axes)
        st.pyplot(fig)

#registered user
with tab2 : 
    
    st.subheader("Registered User")
    col_registered1, col_registered2 = st.columns(2)
    #registered user statistics
    with col_registered1:
        total_rent = df['registered'].sum()
        st.metric("Total:", value=total_rent)

    with col_registered2:
        avg_rent = round(df['registered'].mean(),0)
        st.metric("Avg. rent:", value=avg_rent)
    
    #registered user intensity
    st.subheader("Registered User Intensity")
    st.write('*The number is normalized by divide it with 10000')

    df_transform = transform_heatmap(df,'registered')

    fig,axes = plt.subplots(figsize = (16,10))

    sns.heatmap(df_transform, axes = axes,annot = True)

    st.pyplot(fig)

    st.subheader("Highest Total Rent Based On Date Parameter")

    #casual user highest value by month, days and year

    with st.container():
        st.subheader("Month")
        fig,axes = plt.subplots(figsize = (10,6))
        grouped = grouped_columns(df,'month','registered')
        colors = get_color(grouped)
        plot_image = grouped.plot(kind = 'bar',color = colors,axes = axes)
        plot_image.set_xticklabels(plot_image.get_xticklabels(), rotation=30)
        st.pyplot(fig)

    with st.container():
        st.subheader("Weekday")
        fig,axes = plt.subplots(figsize = (10,6))
        grouped = grouped_columns(df,'weekday','registered')
        colors = get_color(grouped)
        plot_image = grouped.plot(kind = 'bar',color = colors,axes = axes)
        plot_image.set_xticklabels(plot_image.get_xticklabels(), rotation=30)
        st.pyplot(fig)

    with st.container():
        st.subheader("Year")
        fig,axes = plt.subplots(figsize = (10,6))
        grouped = grouped_columns(df,'year','registered')
        colors = get_color(grouped)
        grouped.plot(kind = 'barh',color = colors,axes = axes)
        st.pyplot(fig)









