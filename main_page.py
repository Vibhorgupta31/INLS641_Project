#Library Imports

# Streamlit imports 
import streamlit as st
import streamlit.components.v1 as components
from streamlit_lottie import st_lottie
from streamlit_folium import st_folium

# Visualization libraries
import plotly.express as px
import plotly.graph_objects as go
from bokeh.layouts import column, gridplot
from bokeh.models import ColumnDataSource, RangeTool
from bokeh.plotting import figure, show

# Other library import
import requests
import datetime
import numpy as np
import pandas as pd

#Setting layout of the page
st.set_page_config(layout = "wide") 

# Animaiton Loader Function
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_covid = load_lottieurl('https://assets10.lottiefiles.com/packages/lf20_CXxysN.json')

st.subheader("INLS641: Visual Analytics")
st.subheader("Impact of Covid on hospitals")
st.markdown("*Team: Viola Goodacre, Vibhor Gupta*")

#Data processing
df = pd.read_csv("trimmed_data.csv")
df = df.dropna()
df["date"] = pd.to_datetime(df["date"])
df["date"] = df["date"].dt.date
df = df.iloc[:,[0,1,4,6,9,12]]
min_date = df["date"].min()
max_date = df["date"].max()
list_of_columns = list(df.columns)[2:]
list_of_columns = [(" ".join(column.split("_"))).title() for column in list_of_columns]

with st.sidebar:
  st_lottie(lottie_covid, speed=1.5, width=200, height=200)
  date = st.date_input("Select the date range", value = [min_date, max_date], min_value = min_date, max_value = max_date )
  metric = st.selectbox("What metric you want to view?",list_of_columns)
  metric_column = ("_".join(metric.split(" ")).lower())

# Data filtering and grouping
df = df[(df["date"] >= date[0]) & (df["date"] <= date[1])]
time_plot_data = df.groupby(["date"], as_index = False ).median()
state_data = df.groupby(["state"], as_index = False ).median()
state_data['text'] = state_data['state'] + '<br>' + \
    'Bed Utilization ' + state_data['inpatient_bed_covid_utilization'].round(2).astype(str) + '<br>' + \
    ' Staff Short Today ' + state_data['critical_staffing_shortage_today_yes'].astype(str) + '<br>' + \
    ' Staff Shortage Week ' + state_data['critical_staffing_shortage_anticipated_within_week_yes'].astype(str) + '<br>' + \
    'Covid Deaths ' + state_data['deaths_covid'].astype(str) 

# Tab creation  
about, dashboard, = st.tabs(["About", "Dashboard"])

with about:

	st.markdown("put few lines from the reports and a link for the report to download")

with dashboard :
	st.markdown("**Notes:**")
	st.markdown("""<p align="justify"><ul>
		<li> For the timesereis graph the data is aggregated on day level and the median values are presented </li>
		<li> For the  map the data is aggregated on state level and the median values are presented </li>
		</ul>
		</p>""", unsafe_allow_html=True)

	st.markdown(f"*Distribution of {metric} across time*")

# Timeseries Plot
	dates = np.array(time_plot_data['date'], dtype=np.datetime64)	
	source = ColumnDataSource(data=dict(date=dates, close=time_plot_data[metric_column]))

	p = figure(height=300, width=800, tools="xpan", toolbar_location=None,
	           x_axis_type="datetime", x_axis_location="below",
	           background_fill_color="#ffffff", x_range=(dates[0], dates[-1]))

	p.line('date', 'close', source=source)
	p.yaxis.axis_label = metric
	p.xaxis.axis_label = "Dates"
	st.bokeh_chart(p)

# Map Plot
	st.markdown(f"*Distribution of {metric} across the US*")
	fig = go.Figure(data=go.Choropleth(
      locations=state_data["state"], # Spatial coordinates
      z = state_data[metric_column].astype(float).round(2), # Data to be color-coded
      locationmode = 'USA-states', # set of locations match entries in `locations`
      colorscale = 'Blues',
      text = state_data["text"],
      marker_line_color = 'white',
      colorbar_title = (metric
  )))
	fig.update_layout(
      geo_scope='usa', # limit map scope to USA
  )
	fig.update_layout(autosize = False,
		width = 800,
		)
	st.plotly_chart(fig)
