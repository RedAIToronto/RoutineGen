import streamlit as st
import requests
import json
import pandas as pd
import base64

API_URL = "https://www.stack-inference.com/run_deployed_flow?flow_id=64b093281e40768646b97c6d&org=3d86490f-028d-4c8f-85fe-14e4beb31134"
HEADERS = {
    'Authorization': 'Bearer 7f1a10e9-d642-4dc0-919d-8242a9db099d',
    'Content-Type': 'application/json'
}


def to_csv(schedule_json):
    rows = []
    for day, schedule in schedule_json.items():
        for time, activity in schedule.items():
            row = {
                "Day": day,
                "Time": time,
                "Task": activity
            }
            rows.append(row)
    return pd.DataFrame(rows).to_csv(index=False)


def download_link(csv, filename):
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download CSV File</a>'
    return href


st.title("Weekly Schedule Generator")
st.sidebar.header("Schedule Preferences")
# Radio button for Night Owl or Early Bird
schedule_type = st.sidebar.radio("Select your preference:", options=["Early Bird", "Night Owl"], key="schedule_type")

# Slider for intensity of the schedule
intensity = st.sidebar.slider("Select the intensity of the schedule:", min_value=0, max_value=10, value=5)

prompt = st.text_area("Enter your prompt:")

# Radio button for School or Full-time Job
responsibility = st.sidebar.radio("Do you have school or a full-time job?", options=["None", "School", "Full-time Job"], key="responsibility")

# Conditionally show input fields based on the selection
start_time = None
end_time = None
if responsibility != "None":
    st.sidebar.markdown(f"Enter {responsibility} hours:")
    start_time = st.sidebar.time_input("Start time:", value=pd.Timestamp("09:00"), key="start_time")  # Default 9 AM
    end_time = st.sidebar.time_input("End time:", value=pd.Timestamp("17:00"), key="end_time")        # Default 5 PM

if st.button("Generate Schedule"):
    # Combine the responsibility and timing into a single string
    responsibility_detail = f"{responsibility}-{start_time.strftime('%I:%M %p') if start_time else ''}-{end_time.strftime('%I:%M %p') if end_time else ''}"

    # Include the selected schedule type, intensity, and responsibility detail in the payload
    payload = {
        "in-0": prompt,
        "in-1": responsibility_detail,
        "in-2": intensity
    }
    response = requests.post(API_URL, headers=HEADERS, json=payload)

    if response.status_code == 200:
        schedule_json = json.loads(response.json().get("out-0", ""))

        # Loop through the days in the schedule
        for day, time_slots in schedule_json.items():
            st.subheader(day)

            # Loop through the time slots for each day
            for time, content in time_slots.items():
                st.markdown(f"**{time}:** {content}")
    else:
        st.warning(f"An error occurred while fetching the schedule. Status code: {response.status_code}")
        st.text(response.text)  # Print the response content
    csv = to_csv(schedule_json)
    st.markdown(download_link(csv, "schedule.csv"), unsafe_allow_html=True)
