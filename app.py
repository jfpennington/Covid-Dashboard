import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Page config
st.set_page_config(
    page_title="COVID-19 Dashboard",
    layout="wide"
)

# Load data
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv"
    df = pd.read_csv(url)
    df['date'] = pd.to_datetime(df['date'])
    return df

df = load_data()
countries_df = df[df['continent'].notna()].copy()
world = df[df['location'] == 'World'].copy()
latest = countries_df.groupby('location').last().reset_index()

# Header
st.title("COVID-19 Global Dashboard")
st.markdown("Data source: [Our World in Data](https://ourworldindata.org/covid-cases)")

# Top metrics row
col1, col2, col3, col4 = st.columns(4)
with col1:
    total_cases = latest['total_cases'].sum()
    st.metric("Total Cases", f"{total_cases/1e9:.2f}B")
with col2:
    total_deaths = latest['total_deaths'].sum()
    st.metric("Total Deaths", f"{total_deaths/1e6:.1f}M")
with col3:
    avg_vaxx = latest['people_vaccinated_per_hundred'].mean()
    st.metric("Avg Vaccination Rate", f"{avg_vaxx:.1f}%")
with col4:
    countries_count = latest['location'].nunique()
    st.metric("Countries Tracked", countries_count)

st.divider()

# Section 1 - Global trend
st.subheader("Global new cases over time")
metric_option = st.selectbox(
    "Select metric",
    ['new_cases_smoothed', 'new_deaths_smoothed', 'new_vaccinations_smoothed']
)

fig1 = px.line(world, x='date', y=metric_option, 
               title=f'Global {metric_option.replace("_", " ")} over time')
fig1.update_layout(height=400)
st.plotly_chart(fig1, use_container_width=True)

st.divider()

# Section 2 - Country comparison
st.subheader("Compare countries")
all_countries = sorted(countries_df['location'].unique().tolist())
selected_countries = st.multiselect(
    "Select countries to compare",
    all_countries,
    default=['United States', 'United Kingdom', 'India', 'Brazil', 'Germany']
)

compare_metric = st.selectbox(
    "Select comparison metric",
    ['new_cases_smoothed_per_million', 'new_deaths_smoothed_per_million',
     'people_vaccinated_per_hundred', 'total_cases_per_million']
)

if selected_countries:
    compare_df = countries_df[countries_df['location'].isin(selected_countries)]
    fig2 = px.line(compare_df, x='date', y=compare_metric,
                   color='location',
                   title=f'{compare_metric.replace("_", " ")} by country')
    fig2.update_layout(height=400)
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

# Section 3 - Country deep dive
st.subheader("Country deep dive")
selected_country = st.selectbox("Select a country", all_countries)

country_data = countries_df[countries_df['location'] == selected_country]
latest_country = latest[latest['location'] == selected_country].iloc[0]

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Cases", f"{latest_country['total_cases']:,.0f}")
with col2:
    st.metric("Total Deaths", f"{latest_country['total_deaths']:,.0f}")
with col3:
    vaxx = latest_country['people_vaccinated_per_hundred']
    st.metric("Vaccination Rate", f"{vaxx:.1f}%" if pd.notna(vaxx) else "N/A")

fig3 = px.bar(country_data, x='date', y='new_cases_smoothed',
              title=f'{selected_country} - daily new cases')
fig3.update_layout(height=350)
st.plotly_chart(fig3, use_container_width=True)

st.divider()

# Section 4 - Top countries table
st.subheader("Top 20 countries by total cases")
top20 = latest.nlargest(20, 'total_cases')[
    ['location', 'total_cases', 'total_deaths',
     'people_vaccinated_per_hundred']
].round(1)
top20.columns = ['Country', 'Total Cases', 'Total Deaths', 'Vaccinated (%)']
st.dataframe(top20, use_container_width=True, hide_index=True)