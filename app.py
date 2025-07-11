import streamlit as st
import pandas as pd

# Load data from published Google Sheet (CSV format)
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR93pV70edSHdZnWKBpyvvCoBsZ0JLIpA1qzwM_62vB7qVV8hA6e8_m78q7Oouwk_2fxAK--kNcrwn9/pub?output=csv"
df = pd.read_csv(sheet_url)

# Convert 'Date' column to datetime
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

# Convert numeric columns safely
numeric_cols = ["Reach", "Likes", "Comments", "Shares", "Saves", "Follows"]
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Sidebar filters
st.sidebar.header("Filters")
date_range = st.sidebar.date_input("Select Date Range", [df["Date"].min(), df["Date"].max()])
post_types = ["All"] + sorted(df["Post Type"].dropna().unique().tolist())
selected_type = st.sidebar.selectbox("Select Post Type", post_types)

# Filter data
if len(date_range) == 2:
    df = df[(df["Date"] >= pd.to_datetime(date_range[0])) & (df["Date"] <= pd.to_datetime(date_range[1]))]
if selected_type != "All":
    df = df[df["Post Type"] == selected_type]

st.title("Instagram Analytics Dashboard")

# Summary Metrics
st.subheader("Summary Metrics")
col1, col2, col3 = st.columns(3)
col1.metric("Total Reach", int(df["Reach"].sum()))
col2.metric("Avg Engagements/Post", round((df[["Likes", "Comments", "Shares", "Saves"]].sum(axis=1)).mean(), 2))
col3.metric("New Followers", int(df["Follows"].sum()))

# Bar Chart: Engagement by Post
st.subheader("Engagement by Post")
df["Post Label"] = df["Date"].dt.strftime("%Y-%m-%d") + " | " + df["Post Type"]
df["Engagement Total"] = df[["Likes", "Comments", "Shares", "Saves"]].sum(axis=1)
engagement_by_post = df[["Post Label", "Engagement Total"]].sort_values(by="Engagement Total", ascending=True)
st.bar_chart(data=engagement_by_post.set_index("Post Label"))

# Bar Chart: Average Reach by Post Type
st.subheader("Average Reach by Post Type")
avg_reach = df.groupby("Post Type")["Reach"].mean().sort_values()
st.bar_chart(avg_reach)

# Top Posts Table with clickable links
st.subheader("Top Performing Posts")
df["Instagram Link"] = df["Post URL"].apply(lambda x: f"[View Post]({x})" if pd.notnull(x) and x != "" else "")
top_posts = df.sort_values(by="Engagement Total", ascending=False).head(10)
st.write(top_posts[[
    "Date", "Post Type", "Reach", "Likes", "Comments", "Shares", "Saves", "Engagement Total", "Instagram Link"
]])