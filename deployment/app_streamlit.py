import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

### Config
st.set_page_config(
    page_title="Getaround Dashboard",
    page_icon="🚗",
    layout="wide"
)

DATA_URL = ('https://bucket-getaround-project.s3.eu-west-3.amazonaws.com/get_around_delay_analysis.xlsx')


### App
st.title("Getaround Dashboard 🚗")

st.markdown("""
    This dashboard is made to find the right trade-off between solving the late checkout issue and the hurting of Getaround/owners revenues.
""")

st.markdown("---")

st.subheader('Data')

@st.cache
def load_data():
    data = pd.read_excel(DATA_URL)
    return data

dataset = load_data()

if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(dataset)


### Keep the data with only rentals that have previous rentals and complete the columns (see corresponding notebook for details)

mask = (dataset['previous_ended_rental_id'].isnull() == False)
df_previous = dataset[mask].copy()

def get_previous_info(r_id) :
    previous_index = dataset['rental_id'].loc[lambda x: x==r_id].index[0]
    return [dataset.loc[previous_index,'delay_at_checkout_in_minutes'], dataset.loc[previous_index,'checkin_type']]

df_previous['previous_delay_at_checkout_in_minutes'],  df_previous['previous_checkin_type'] = zip(*df_previous['previous_ended_rental_id'].apply(get_previous_info))

df_previous['delay_checkin'] = df_previous['previous_delay_at_checkout_in_minutes'] - df_previous['time_delta_with_previous_rental_in_minutes']
df_previous['late_checkin'] = df_previous['delay_checkin'].apply(lambda x : 1 if x > 0 else 0)


### Statistics on canceled and late rentals

st.markdown("---")
st.subheader('Canceled and late rentals')

col1, col2 = st.columns(2)

with col1:
    # proportion of canceled rentals for the whole rentals
    fig = px.sunburst(pd.DataFrame(dataset.groupby(['state', 'checkin_type'], as_index=False).size()),
                        path = ['state', 'checkin_type'],
                        values='size',
                    )
    fig.update_traces(textinfo="label+percent parent")
    fig.update_layout(title={'text': "Proportion of canceled for the whole rentals", 'y':0.95, 'x':0.5, 'xanchor': 'center', 'yanchor': 'top'},
                        autosize=False,
                        height=500,
                        width=500,
                        title_font_color="#D50425")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # proportion of canceled rentals when there is a previous rental
    fig = px.sunburst(pd.DataFrame(df_previous.groupby(['state', 'previous_checkin_type'], as_index=False).size()),
                path = ['state', 'previous_checkin_type'],
                values='size',
                )
    fig.update_traces(textinfo="label+percent parent")
    fig.update_layout(title={'text': "Proportion of canceled rentals when there is a previous rental", 'y':0.95, 'x':0.5, 'xanchor': 'center', 'yanchor': 'top'},
                        autosize=False,
                        height=500,
                        width=500,
                        title_font_color="#D50425")
    st.plotly_chart(fig, use_container_width=True)

col3, col4 = st.columns(2)

with col3 :
    # proportion of late checkin when there is a previous rental
    fig = px.sunburst(pd.DataFrame(df_previous.groupby(['late_checkin', 'previous_checkin_type'], as_index=False).size()),
                path = ['late_checkin', 'previous_checkin_type'],
                values='size',
                )
    fig.update_traces(textinfo="label+percent parent")
    fig.update_layout(title={'text': "Proportion of late checkin when there is a previous rental", 'y':0.95, 'x':0.5, 'xanchor': 'center', 'yanchor': 'top'},
                        autosize=False,
                        height=500,
                        width=500,
                        title_font_color="#D50425")
    st.plotly_chart(fig, use_container_width=True)

with col4 :
    mask = df_previous['late_checkin'] == 1
    df_late = df_previous[mask].copy()
    # proportion of canceled rentals when late checkin
    fig = px.sunburst(pd.DataFrame(df_late.groupby(['state', 'checkin_type'], as_index=False).size()),
                path = ['state', 'checkin_type'],
                values='size',
                )
    fig.update_traces(textinfo="label+percent parent")
    fig.update_layout(title={'text': "Proportion of canceled rentals when late checkin", 'y':0.95, 'x':0.5, 'xanchor': 'center', 'yanchor': 'top'},
                        autosize=False,
                        height=500,
                        width=500,
                        title_font_color="#D50425")
    st.plotly_chart(fig, use_container_width=True)


### Distribution of time delta between 2 rentals
st.markdown("---")
st.subheader('Distribution of time delta between 2 rentals')

df_temp = df_previous.groupby(['time_delta_with_previous_rental_in_minutes', 'checkin_type'], as_index = False).sum()

fig = px.bar(df_temp, x = 'time_delta_with_previous_rental_in_minutes', y = 'late_checkin', color = 'checkin_type')
fig.update_layout(title={'text': "Number of late check-ins depending on time delta between 2 rentals", 'y':0.95, 'x':0.5, 'xanchor': 'center', 'yanchor': 'top'},
                    title_font_color="#D50425")
st.plotly_chart(fig, use_container_width=True)


### Prepare the dataset for further analysis

thresholds = list(range(0, 750, 30))

def checkin_solved(previous_delay, threshold, state, late_next_checkin) :      # determine if the rental was canceled when there is late previous checkout and if it will be solved with the threshold
    if (late_next_checkin == 1) & (state == 'canceled') & (previous_delay < threshold) :
        return 1
    else :
        return 0

def late_solved(previous_delay, threshold, late_next_checkin) :      # determine if the rental was in danger due to late previous checkout and if it will be solved with the threshold
    if (late_next_checkin == 1) & (previous_delay < threshold) :
        return 1
    else :
        return 0

for item in thresholds :
    df_previous[f'threshold_{item}'] = df_previous['time_delta_with_previous_rental_in_minutes'].apply(lambda x : 1 if x < item else 0) # no effect if the time delta is less than the threshold
    df_previous[f'checkin_solved_{item}'] = list(map(checkin_solved, df_previous['previous_delay_at_checkout_in_minutes'], [item] * df_previous.shape[0], df_previous['state'], df_previous['late_checkin'])) # find canceled rentals that would be solved with the threshold
    df_previous[f'late_solved_{item}'] = list(map(late_solved, df_previous['previous_delay_at_checkout_in_minutes'], [item] * df_previous.shape[0], df_previous['late_checkin'])) # find late rentals that would be solved with the threshold

df_temp = df_previous.groupby(['checkin_type'], as_index=False).sum()
df_temp.loc[2,:] = df_temp.iloc[0,:] + df_temp.iloc[1,:]
df_temp.loc[2,'checkin_type'] = 'connect + mobile'

df_temp = pd.melt(df_temp, id_vars=['checkin_type'], var_name='impacts', value_name='nb_affected')

# select only the total cases that would be impacted by a threshold
df_temp_total = df_temp[df_temp['impacts'].str.contains('threshold', case=False, regex=False)].copy()
df_temp_total['thresholds'] = df_temp_total['impacts'].apply(lambda x : x.split('_')[1])

# select only the cases that were canceled and that would be impacted by a threshold
df_temp_canceled = df_temp[df_temp['impacts'].str.contains('checkin_solved', case=False, regex=False)].copy()
df_temp_canceled['thresholds'] = df_temp_canceled['impacts'].apply(lambda x : x.split('_')[2])

# select only the cases with previous late checkout and that would be impacted by a threshold
df_temp_late = df_temp[df_temp['impacts'].str.contains('late_solved', case=False, regex=False)].copy()
df_temp_late['thresholds'] = df_temp_late['impacts'].apply(lambda x : x.split('_')[2])

# in terms of revenue, we assume that all the rentals are under an average price, that is the percentage of rentals affected = the percentage of revenue affected
df_temp_total['affected_revenue_in_percent_total_rentals'] = df_temp_total['nb_affected'] / dataset.shape[0] * 100
df_temp_total['affected_revenue_in_percent_successive_rentals'] = df_temp_total['nb_affected'] / df_previous.shape[0] * 100


### Impacts with thresholds from 0 to 720 min
st.markdown("---")
st.subheader('Impacts with thresholds from 0 to 720 min')

col1, col2, col3 = st.columns(3)

with col1 :
    fig = px.line(df_temp_total, x = 'thresholds', y = 'nb_affected',
                    markers = True,
                    color = 'checkin_type'
                )
    fig.update_layout(yaxis_title='Number of rentals affected',
                        xaxis_title='Level of threshold in min',
                        legend_title = 'Type of check-in',
                        title={'text': "Number of rentals affected by a threshold", 'y':0.95, 'x':0.5, 'xanchor': 'center', 'yanchor': 'top'},
                        autosize=False,
                        height=500,
                        width=1000,
                        title_font_color="#D50425")
    st.plotly_chart(fig, use_container_width=True)

with col2 :
    fig = px.line(df_temp_canceled, x = 'thresholds', y = 'nb_affected',
                    markers = True,
                    color = 'checkin_type'
                )
    fig.update_layout(yaxis_title='Number of rentals affected',
                        xaxis_title='Level of threshold in min',
                        legend_title = 'Type of check-in',
                        title={'text': "Number of canceled rentals that could be avoided", 'y':0.95, 'x':0.5, 'xanchor': 'center', 'yanchor': 'top'},
                        autosize=False,
                        height=500,
                        width=1000,
                        title_font_color="#D50425")
    st.plotly_chart(fig, use_container_width=True)

with col3 :
    fig = px.line(df_temp_late, x = 'thresholds', y = 'nb_affected',
                    markers = True,
                    color = 'checkin_type'
                )
    fig.update_layout(yaxis_title='Number of rentals affected',
                        xaxis_title='Level of threshold in min',
                        legend_title = 'Type of check-in',
                        title={'text': "Number of late checkout that would not impact a successive rental", 'y':0.95, 'x':0.5, 'xanchor': 'center', 'yanchor': 'top'},
                        autosize=False,
                        height=500,
                        width=1000,
                        title_font_color="#D50425")
    st.plotly_chart(fig, use_container_width=True)

col4, col5 = st.columns(2)

with col4 :
    fig = px.line(df_temp_total, x = 'thresholds', y = 'affected_revenue_in_percent_total_rentals',
                    markers = True,
                    color = 'checkin_type'
                )
    fig.update_layout(yaxis_title='Number of rentals affected',
                        xaxis_title='Level of threshold in min',
                        legend_title = 'Type of check-in',
                        title={'text': "Percentage of total revenue affected by a threshold", 'y':0.95, 'x':0.5, 'xanchor': 'center', 'yanchor': 'top'},
                        autosize=False,
                        height=500,
                        width=1000,
                        title_font_color="#D50425")
    st.plotly_chart(fig, use_container_width=True)

with col5 :
    fig = px.line(df_temp_total, x = 'thresholds', y = 'affected_revenue_in_percent_successive_rentals',
                    markers = True,
                    color = 'checkin_type'
                )
    fig.update_layout(yaxis_title='Number of rentals affected',
                        xaxis_title='Level of threshold in min',
                        legend_title = 'Type of check-in',
                        title={'text': "Percentage of revenue from rentals that have previous rentals that would be affected by a threshold", 'y':0.95, 'x':0.5, 'xanchor': 'center', 'yanchor': 'top'},
                        autosize=False,
                        height=500,
                        width=1000,
                        title_font_color="#D50425")
    st.plotly_chart(fig, use_container_width=True)

