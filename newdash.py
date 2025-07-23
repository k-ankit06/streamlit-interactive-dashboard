import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import warnings
import os

warnings.filterwarnings("ignore")

st.set_page_config(page_title="Universal Data Dashboard", page_icon=":bar_chart:", layout="wide")

st.title(":bar_chart: Universal Exploratory Data Analysis")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)

fl = st.file_uploader(":file_folder: Upload your Dataset", type=["csv", "txt", "xlsx", "xls"])

if fl is not None:
    filename = fl.name
    try:
        if filename.endswith(".csv") or filename.endswith(".txt"):
            df = pd.read_csv(fl, encoding="ISO-8859-1")
        else:
            df = pd.read_excel(fl)
        st.success("✅ File loaded successfully!")
    except Exception as e:
        st.error(f"❌ File loading failed: {e}")
        st.stop()
else:
    st.info("Using default sample dataset...")
    os.chdir(r"C:\Users\cdick\OneDrive\Desktop\Interactive Dashbaord")
    df = pd.read_csv("Sample - Superstore.csv", encoding="ISO-8859-1")

st.write("Available Columns:", df.columns.tolist())

required_cols = ["Order Date", "Region", "State", "City", "Category", "Sales", "Profit", "Quantity", "Segment", "Sub-Category"]
missing = [col for col in required_cols if col not in df.columns]

if missing:
    st.warning(f"⚠️ Missing columns: {missing}. Some sections may be disabled.")

if "Order Date" in df.columns:
    try:
        df["Order Date"] = pd.to_datetime(df["Order Date"])
        startDate = df["Order Date"].min()
        endDate = df["Order Date"].max()

        col1, col2 = st.columns(2)
        with col1:
            date1 = pd.to_datetime(st.date_input("Start Date", startDate))
        with col2:
            date2 = pd.to_datetime(st.date_input("End Date", endDate))

        df = df[(df["Order Date"] >= date1) & (df["Order Date"] <= date2)]
    except:
        st.warning("Order Date conversion failed.")

st.sidebar.header("Choose Your Filters")

filtered_df = df.copy()
if "Region" in df.columns:
    region = st.sidebar.multiselect("Pick Region", df["Region"].unique())
    if region:
        filtered_df = filtered_df[filtered_df["Region"].isin(region)]

if "State" in df.columns:
    state = st.sidebar.multiselect("Pick State", filtered_df["State"].unique())
    if state:
        filtered_df = filtered_df[filtered_df["State"].isin(state)]

if "City" in df.columns:
    city = st.sidebar.multiselect("Pick City", filtered_df["City"].unique())
    if city:
        filtered_df = filtered_df[filtered_df["City"].isin(city)]

if "Category" in df.columns and "Sales" in df.columns:
    category_df = filtered_df.groupby("Category", as_index=False)["Sales"].sum()
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Sales by Category")
        fig = px.bar(category_df, x="Category", y="Sales", text_auto=".2s", template="seaborn")
        st.plotly_chart(fig, use_container_width=True)

if "Region" in df.columns and "Sales" in df.columns:
    with col2:
        st.subheader("Sales by Region")
        region_df = filtered_df.groupby("Region", as_index=False)["Sales"].sum()
        fig = px.pie(region_df, names="Region", values="Sales", hole=0.4)
        st.plotly_chart(fig, use_container_width=True)

if "Order Date" in df.columns and "Sales" in df.columns:
    filtered_df["month_year"] = filtered_df["Order Date"].dt.to_period("M")
    st.subheader("Time Series Sales Analysis")
    ts_df = filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y-%m"))["Sales"].sum().reset_index()
    fig2 = px.line(ts_df, x="month_year", y="Sales", labels={"Sales": "Amount"}, template="gridon")
    st.plotly_chart(fig2, use_container_width=True)

if set(["Region", "Category", "Sub-Category", "State", "Sales"]).issubset(df.columns):
    st.subheader("Hierarchical view of Sales")
    fig3 = px.treemap(filtered_df, path=["Region", "Category", "Sub-Category", "State"], values="Sales",
                      color="Sub-Category", color_continuous_scale="RdBu")
    st.plotly_chart(fig3, use_container_width=True)

chart1, chart2 = st.columns(2)
if "Segment" in df.columns and "Sales" in df.columns:
    with chart1:
        st.subheader("Segment-wise Sales")
        fig = px.pie(filtered_df, names="Segment", values="Sales", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

if "Category" in df.columns and "Sales" in df.columns:
    with chart2:
        st.subheader("Category-wise Sales")
        fig = px.pie(filtered_df, names="Category", values="Sales", template="gridon")
        st.plotly_chart(fig, use_container_width=True)

st.subheader(":point_right: Sample Data View")
with st.expander("Data Table and Summary"):
    try:
        df_sample = df.head(5)[["Region", "State", "City", "Category", "Sales", "Profit", "Quantity"]]
        fig_table = ff.create_table(df_sample, colorscale="Cividis")
        st.plotly_chart(fig_table, use_container_width=True)
    except:
        st.info("Table cannot be created (columns missing).")

    if "Order Date" in df.columns and "Sub-Category" in df.columns:
        filtered_df["month"] = filtered_df["Order Date"].dt.month_name()
        try:
            pivot_table = pd.pivot_table(filtered_df, values="Sales", index=["Sub-Category"], columns="month")
            st.write(pivot_table.style.background_gradient(cmap="Blues"))
        except:
            st.info("Pivot table failed.")

if set(["Sales", "Profit", "Quantity"]).issubset(df.columns):
    st.subheader("Relationship between Sales and Profit")
    scatter = px.scatter(filtered_df, x="Sales", y="Profit", size="Quantity", color="Category" if "Category" in df.columns else None)
    scatter.update_layout(
        title={"text": "Sales vs Profit", "font": {"size": 20}},
        xaxis={"title": {"text": "Sales", "font": {"size": 18}}},
        yaxis={"title": {"text": "Profit", "font": {"size": 18}}}
    )
    st.plotly_chart(scatter, use_container_width=True)
with st.expander("View Raw Data"):
    st.write(filtered_df.style.background_gradient(cmap="Oranges"))

csv = df.to_csv(index=False).encode("utf-8")
st.download_button("Download Full Dataset", data=csv, file_name="cleaned_data.csv", mime="text/csv")