import pandas as pd

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Set the page configuration
st.set_page_config(layout="wide")




# Load the dataset
@st.cache_data  # Cache the data to improve performance
def load_data():
    df = pd.read_excel('src/get_around_delay_analysis.xlsx', sheet_name='rentals_data')  
    return df

df = load_data()


Q1 = df["delay_at_checkout_in_minutes"].quantile(0.25)
Q3 = df["delay_at_checkout_in_minutes"].quantile(0.75)
IQR = Q3 - Q1
# Streamlit App Title
st.title("Getaround Rental Analysis")
st.write("Explore how different thresholds and scopes affect rental delays and revenue.")

# Handle Outliers
st.sidebar.header("Outlier Handling")

outlier_bound = st.sidebar.slider("Select outlier bounds:", min_value=1.5, max_value=6.0, value=1.5, step=0.1)
lower_bound = Q1 - IQR * outlier_bound
upper_bound = Q3 + IQR * outlier_bound
st.sidebar.write(f"Retain values between {lower_bound} and {upper_bound}")
df_no_outliers = df.copy()
df_no_outliers["delay_at_checkout_in_minutes"] = df_no_outliers["delay_at_checkout_in_minutes"].apply(lambda x : x if x >= lower_bound and x <= upper_bound else float("nan"))  # Remove delays > 1 day
affected_rows =  df_no_outliers["delay_at_checkout_in_minutes"].isna().sum() - df["delay_at_checkout_in_minutes"].isna().sum()
st.sidebar.write(f"{affected_rows} rows will be affected, accounting for {(affected_rows / len(df) * 100):.2f}% of the total.")

outlier_method = st.sidebar.selectbox(
    "Choose Outlier Handling Method:",
    ["Remove Outliers", "Cap Outliers", "Input median", "Input mean", "None"]
)

if outlier_method == "Remove Outliers":
    df = df_no_outliers
elif outlier_method == "Cap Outliers":
    df['delay_at_checkout_in_minutes'] = df['delay_at_checkout_in_minutes'].clip(lower=lower_bound, upper=upper_bound)  # Cap at 1 day
elif outlier_method == "Input median":
    median = df["delay_at_checkout_in_minutes"].median()
    df['delay_at_checkout_in_minutes'] = df['delay_at_checkout_in_minutes'].apply(lambda x : median if x < lower_bound or x > upper_bound else x)
elif outlier_method == "Input mean":
    mean = df["delay_at_checkout_in_minutes"].mean()
    df['delay_at_checkout_in_minutes'] = df['delay_at_checkout_in_minutes'].apply(lambda x : mean if x < lower_bound or x > upper_bound else x)

fig = px.violin(df,x="delay_at_checkout_in_minutes", title="delay at checkout distribution")
fig.update_layout(
    xaxis=dict(
        title='delay at checkout in minutes'
    )
)
st.plotly_chart(fig)

# geting previous checkout delay if available
df["previous_rental_delay_at_checkout_in_minutes"] = df["previous_ended_rental_id"].apply(lambda x : df[df["rental_id"] == x]["delay_at_checkout_in_minutes"].iloc[0] if len(df[df["rental_id"] == x]) > 0 else None)
# calculating if car was late
df["time_delta_since_car_last_checkout_in_minutes"] = df["previous_rental_delay_at_checkout_in_minutes"]  - df["time_delta_with_previous_rental_in_minutes"]
df["car_is_late_for_next_checkin"] = df["time_delta_since_car_last_checkout_in_minutes"].apply(lambda x : x > 0) 


canceled_rentals_given_late = df[(df["time_delta_since_car_last_checkout_in_minutes"].notna()) & (df["car_is_late_for_next_checkin"])]["state"].apply(lambda x : True if x == "canceled" else False).mean() * 100
canceled_rentals_given_not_late = df[(df["time_delta_since_car_last_checkout_in_minutes"].notna()) & (df["car_is_late_for_next_checkin"] == False)]["state"].apply(lambda x : True if x == "canceled" else False).mean() * 100
# Create the initial bar plot
fig = go.Figure()
fig.add_trace(go.Bar(
        x=["on time"],
        y=[canceled_rentals_given_not_late]
    ))
fig.add_trace(go.Bar(
        x=["late (any delay)"],
        y=[canceled_rentals_given_late]
    ))
step = 50
# Add bars using a loop
for i in range(0,200,step):
    canceled_rentals_given_late_from_i = df[(df["time_delta_since_car_last_checkout_in_minutes"] >= i) & (df["time_delta_since_car_last_checkout_in_minutes"] < i + step)]["state"].apply(lambda x : True if x == "canceled" else False).mean() * 100
    fig.add_trace(go.Bar(
        x=[f"{i}-{i+step}"],
        y=[canceled_rentals_given_late_from_i]
    ))
fig.update_layout(
    title="Analyzing the impact of check-in delays on cancellation rates",
    xaxis_title='Delay in minutes',
    yaxis_title='Cancellation Percentage',
    showlegend = False
)
fig.show()
st.plotly_chart(fig)
st.write(f"Rentals are {canceled_rentals_given_late - canceled_rentals_given_not_late : 0.2f}% more likely to be canceled if the car is not ready on time.")

st.sidebar.header(f"Set a minimum interval between rentals and observe its impact")
# Sidebar for User Input
threshold_connect = st.sidebar.slider("Select Threshold for connect checkin (minutes):", min_value=0, max_value=180, value=60, step=30)
threshold_mobile = st.sidebar.slider("Select Threshold for mobile checkin (minutes):", min_value=0, max_value=180, value=60, step=30)

# Calculate Metrics
df_delay = df.loc[df["delay_at_checkout_in_minutes"].notna(),:].copy() # Removing rows without checkout delay (also remove all canceled rentals)
df_len = len(df)
df_delay_len = len(df_delay)
# connect
df_connect = df.loc[df["checkin_type"] == "connect"]
df_delay_connect = df_delay.loc[df_delay["checkin_type"] == "connect"]
df_connect_len = len(df_connect)
df_delay_connect_len = len(df_delay_connect)
# mobile
df_mobile = df.loc[df["checkin_type"] == "mobile"]
df_delay_mobile = df_delay.loc[df_delay["checkin_type"] == "mobile"]
df_mobile_len = len(df_mobile)
df_delay_mobile_len = len(df_delay_mobile)

df_thresholds = pd.DataFrame({"threshold" : [i for i in range(0,241,30) ]})
df_thresholds["share_affected_connect"] = df_thresholds["threshold"].apply(lambda x : len(df_connect[(df_connect["time_delta_with_previous_rental_in_minutes"] < x)])) # Consider NaN values as durations exceeding 12 hours.
df_thresholds["share_affected_percentage_connect"] = df_thresholds["share_affected_connect"].apply(lambda x : x / df_connect_len * 100)
df_thresholds["share_affected_percentage_all_connect"] = df_thresholds["share_affected_connect"].apply(lambda x : x / df_len * 100)
df_thresholds["late_checkout_connect"] = df_thresholds["threshold"].apply(lambda x : len(df_delay_connect[(df_delay_connect["delay_at_checkout_in_minutes"] > x)]))
df_thresholds["late_checkout_probability_connect"] = df_thresholds["late_checkout_connect"].apply(lambda x : x / df_delay_connect_len * 100)
df_thresholds["late_checkout_probability_all_connect"] = df_thresholds["late_checkout_connect"].apply(lambda x : x / df_delay_len * 100)

df_thresholds["share_affected_mobile"] = df_thresholds["threshold"].apply(lambda x : len(df_mobile[(df_mobile["time_delta_with_previous_rental_in_minutes"] < x)])) # Consider NaN values as durations exceeding 12 hours.
df_thresholds["share_affected_percentage_mobile"] = df_thresholds["share_affected_mobile"].apply(lambda x : x / df_mobile_len * 100)
df_thresholds["share_affected_percentage_all_mobile"] = df_thresholds["share_affected_mobile"].apply(lambda x : x / df_len * 100)
df_thresholds["late_checkout_mobile"] = df_thresholds["threshold"].apply(lambda x : len(df_delay_mobile[(df_delay_mobile["delay_at_checkout_in_minutes"] > x)]))
df_thresholds["late_checkout_probability_mobile"] = df_thresholds["late_checkout_mobile"].apply(lambda x : x / df_delay_mobile_len * 100)
df_thresholds["late_checkout_probability_all_mobile"] = df_thresholds["late_checkout_mobile"].apply(lambda x : x / df_delay_len * 100)





# Display Metrics
st.subheader("Key Metrics")

connect_share_affected = df_thresholds[df_thresholds["threshold"] == threshold_connect]["share_affected_percentage_all_connect"].iloc[0]
mobile_share_affected = df_thresholds[df_thresholds["threshold"] == threshold_mobile]["share_affected_percentage_all_mobile"].iloc[0]
unafected_share = 100 - connect_share_affected - mobile_share_affected 

connect_late_probability = df_thresholds[df_thresholds["threshold"] == threshold_connect]["late_checkout_probability_all_connect"].iloc[0]
mobile_late_probability = df_thresholds[df_thresholds["threshold"] == threshold_mobile]["late_checkout_probability_all_mobile"].iloc[0]
on_time = 100 - connect_late_probability - mobile_late_probability 

# Create subplots: 1 row, 2 columns for pie charts
fig = make_subplots(rows=1, cols=2, specs=[[{'type': 'domain'}, {'type': 'domain'}]])



fig.add_trace(go.Pie(labels=["connect","mobile","unaffected"],values=[connect_share_affected, mobile_share_affected, unafected_share], title={'text':'Share affected', 'position': 'bottom center'}, hole=0.6 ),row=1, col=1)
fig.add_trace(go.Pie(labels=["connect","mobile","on time"],values=[connect_late_probability, mobile_late_probability, on_time], title={'text':'Probability to be late for checkin at minimum interval', 'position': 'bottom center'}, hole=0.6 ),row=1, col=2)

fig.add_trace(go.Scatter(x=df_thresholds['threshold'],y=df_thresholds['share_affected_percentage_connect'], name="Share affected (connect)", visible=False ))
fig.add_trace(go.Scatter(x=df_thresholds['threshold'],y=df_thresholds['late_checkout_probability_connect'], name="Probability to be late at minimum interval (connect)", visible=False))

fig.add_trace(go.Scatter(x=df_thresholds['threshold'],y=df_thresholds["share_affected_percentage_mobile"], name="Share affected (mobile)", visible=False ))
fig.add_trace(go.Scatter(x=df_thresholds['threshold'],y=df_thresholds["late_checkout_probability_mobile"], name="Probability to be late at minimum interval (mobile)", visible=False))


fig.add_shape(type='line',
              x0=threshold_connect, x1=threshold_connect,
              y0=0, y1=1,
              yref='paper', line=dict(color='red', width=2),
              visible=False)

fig.add_shape(type='line',
              x0=threshold_mobile, x1=threshold_mobile,
              y0=0, y1=1,
              yref='paper', line=dict(color='red', width=2),
              visible=False)



# Create the layout
layout = go.Layout(
    title="Affected rentals",
    xaxis = {"visible" : False},
    yaxis = {"visible" : False},
    xaxis_title='Threshold in minutes',
    yaxis_title='Affected renatals Percentage',
    updatemenus=[
        {
            
            "buttons": [
                {
                    "label": "Affected rentals",
                    "method": "update",
                    "args": [
                        {"visible": [True, True, False, False, False, False]}, 
                        {
                            "title" : "Affected rentals", 
                            "shapes[0].visible": False, 
                            "shapes[1].visible": False, 
                            "xaxis" : {"visible" : False}, 
                            "yaxis" : {"visible" : False} 
                        }
                    ]
                },
                {
                    "label": "Affected rentals (connect)",
                    "method": "update",
                    "args": [
                        {"visible": [False, False, True, True, False, False]}, 
                        {
                            "title" : "Affected rentals by threshold (connect)", 
                            "shapes[0].visible": True, 
                            "shapes[1].visible": False, 
                            "xaxis" : {"visible" : True, "title": {"text": "Threshold in minutes"}}, 
                            "yaxis" : {"visible" : True, "title": {"text": "Affected rentals Percentage"}}
                        }
                    ]
                },
                {
                    "label": "Affected rentals (mobile)",
                    "method": "update",
                    "args": [
                        {"visible": [False, False, False, False, True, True]}, 
                        {
                            "title" : "Affected rentals by threshold (mobile)", 
                            "shapes[0].visible": False, 
                            "shapes[1].visible": True, 
                            "xaxis" : {"visible" : True, "title": {"text": "Threshold in minutes"}}, 
                            "yaxis" : {"visible" : True, "title": {"text": "Affected rentals Percentage"}}
                        }
                    ]
                }
            ],
            "direction": "down",
            "showactive": True,
        }
    ]
)
# Update layout
fig.update_layout(layout)

st.plotly_chart(fig)