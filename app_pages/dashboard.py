import streamlit as st
import pandas as pd
from utils.db import get_reservations
from datetime import date, timedelta

st.header("📊 Current Schedule")

# Filters
today = date.today()
monday = today - timedelta(days=today.weekday())
sunday = monday + timedelta(days=6)

st.write(f"Showing reservations for the current week: **{monday}** to **{sunday}**")

df = get_reservations(monday.strftime("%Y-%m-%d"), sunday.strftime("%Y-%m-%d"))

if df.empty:
    st.info("No reservations found for this week.")
else:
    df['date'] = pd.to_datetime(df['date']).dt.date
    df = df.sort_values(['date', 'slot_start'])
    
    # Create a group label column
    df['group'] = df['group_type'] + " " + df['group_index'].astype(str)
    
    display_df = df[['date', 'slot_start', 'slot_end', 'group']].copy()
    display_df.columns = ['Date', 'Start', 'End', 'Group']
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)

st.divider()

# Detailed view per day
st.subheader("Daily Breakdown")
view_date = st.date_input("Select a day to view details", value=today)
day_df = get_reservations(view_date.strftime("%Y-%m-%d"), view_date.strftime("%Y-%m-%d"))

if day_df.empty:
    st.write(f"No reservations for {view_date}.")
else:
    day_df['group'] = day_df['group_type'] + " " + day_df['group_index'].astype(str)
    for start, end in day_df[['slot_start', 'slot_end']].drop_duplicates().values:
        slot_groups = day_df[(day_df['slot_start'] == start) & (day_df['slot_end'] == end)]['group'].tolist()
        st.write(f"**{start} - {end}:** {', '.join(slot_groups)}")
