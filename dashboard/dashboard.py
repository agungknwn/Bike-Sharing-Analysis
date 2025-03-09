import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import os


# Helper Functions
def create_weathersit_df(data, weathersit):
    bins = [0, 13, 21, 27, 42]
    labels = ["dingin", "Sejuk", "Hangat", "Panas"]

    data["temp_category"] = pd.cut(
        data["temp_y"], bins=bins, labels=labels, right=False
    )
    weathersit_pivot_df = (
        data.groupby(by=["weathersit_y", "temp_category"])
        .agg({"casual_y": ["mean"], "registered_y": ["mean"], "cnt_y": ["mean"]})
        .reset_index()
    )
    weathersit_pivot_df.columns = [
        "weathersit_daily",
        "temp_category",
        "casual_daily",
        "registered_daily",
        "cnt_daily",
    ]

    weathersit_pivot_df["weathersit_daily"] = pd.Categorical(
        weathersit_pivot_df["weathersit_daily"], weathersit
    )

    return weathersit_pivot_df


def create_usage_trend_df(data, months):
    daily_usage_df = (
        data.groupby(by=["mnth_y"])
        .agg({"registered_y": "mean", "casual_y": "mean", "cnt_y": "mean"})
        .reset_index()
    )
    daily_usage_df.columns = [
        "months",
        "registered_counts",
        "casual_counts",
        "total_counts",
    ]

    daily_usage_df["months"] = pd.Categorical(
        daily_usage_df["months"], months, ordered=True
    )
    daily_usage_plot = daily_usage_df.sort_values(by="months", ascending=True)

    return daily_usage_plot


def create_usage_comparison_df(data):
    usage_comparison_df = (
        data.groupby(by=["workingday_y"])
        .agg({"casual_y": "mean", "registered_y": "mean", "cnt_y": "mean"})
        .reset_index()
    )
    usage_comparison_df.columns = ["day_type", "Casual", "Registered", "Total"]

    usage_comparison_df["day_type"] = usage_comparison_df["day_type"].replace(
        {False: "Holiday", True: "Working Day"}
    )

    usage_comparison_melt_df = usage_comparison_df.melt(
        id_vars=["day_type"], var_name="user_type", value_name="user_counts"
    )

    return usage_comparison_melt_df


def trend_plot(
    data, start_date, end_date, user_counts, markers, linestyles, colors, labels
):
    fig, ax = plt.subplots(figsize=(10, 5))

    for i in range(len(user_counts)):
        ax.plot(
            data["months"],
            data[user_counts[i]],
            marker=markers[i],
            linestyle=linestyles[i],
            color=colors[i],
            label=labels[i],
        )

    # Global plot config:
    ax.set_ylabel("Rata Rata Pengguna Sharing Bike (Harian)")
    ax.set_title(f"Tren Penggunaan Sharing Bike dari {start_date} hingga {end_date}")
    ax.legend()
    ax.grid(True)
    plt.xticks(rotation=45)

    return fig


file_path = os.path.join(os.getcwd(), "main_data.csv")
data = pd.read_csv(file_path)

# Global variables
years = ["2011", "2012"]
months = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]
weathersit = ["Clear", "Mist/Cloudy", "Light Rain/Snow", "Heavy Rain/Snow"]

min_date = data["dteday"].min()
max_date = data["dteday"].max()

with st.sidebar:
    # Membuat slider
    start_date, end_date = st.date_input(
        label="Rentang Waktu",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date],
    )

main_df = data[(data.dteday >= str(start_date)) & (data.dteday <= str(end_date))]

weathersit_df = create_weathersit_df(main_df, weathersit)
usage_trend_df = create_usage_trend_df(main_df, months)
usage_comparison_df = create_usage_comparison_df(main_df)

st.header("Sharing Bike Average Usage Dashboard")
st.subheader(
    f"Daily Usage: {start_date.strftime('%B %d, %Y')} - {end_date.strftime('%B %d, %Y')}"
)

column1, column2 = st.columns(2)
with column1:
    title_col1 = "Total Daily Usage"

    daily_usage = main_df.cnt_y.sum()
    st.metric(title_col1, value=f"{daily_usage:,.0f}")

with column2:
    title_col2 = "Total Hourly Usage"

    hourly_usage = main_df.cnt_x.sum()
    st.metric(title_col2, value=f"{hourly_usage:,.0f}")

tab1, tab2, tab3 = st.tabs(
    ["Weather Analysis", "Usage Trends", "Holiday vs Working Day"]
)

with tab1:

    fig, ax = plt.subplots(figsize=(10, 5))

    sns.barplot(
        data=weathersit_df,
        x="weathersit_daily",
        y="cnt_daily",
        hue="temp_category",
        palette="Set2",
        ax=ax,
    )
    ax.set_xlabel("Kategori Cuaca")
    ax.set_ylabel("Rata Rata Pengguna Sharing Bike (Harian)")
    ax.set_title("Pengaruh Temperatur dan Cuaca Terhadap Penggunaan Sharing Bike")
    ax.legend(title="Temperatur")

    st.pyplot(fig)

with tab2:
    sub_data = ["total_counts", "registered_counts", "casual_counts"]
    markers = ["o", "s", "d"]
    linestyles = ["-", "--", ":"]
    colors = ["r", "g", "b"]
    labels = ["Total", "Registered", "Casual"]
    fig2 = trend_plot(
        usage_trend_df,
        start_date,
        end_date,
        sub_data,
        markers,
        linestyles,
        colors,
        labels,
    )

    st.pyplot(fig2)

with tab3:

    fig3, ax = plt.subplots(figsize=(10, 5))

    sns.barplot(
        data=usage_comparison_df,
        x="day_type",
        y="user_counts",
        hue="user_type",
        palette="Set2",
        ax=ax,
    )
    ax.set_xlabel("Kategori Hari")
    ax.set_ylabel("Rata Rata Pengguna Sharing Bike (Harian)")
    ax.set_title("Penggunaan Sharing Bike: Holiday vs Working Day")
    ax.legend(title="Tipe User")

    st.pyplot(fig3)
