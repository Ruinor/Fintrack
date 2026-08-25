import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

from database import (
    init_db,
    add_expense,
    get_all_expenses,
    delete_expense,
    clear_all_expenses,
    CATEGORIES,
)

st.set_page_config(
    page_title="Fintrack",
    page_icon="",
    layout="centered",  
)

init_db()

st.title("Fintrack💰")
st.caption("Track your daily expenses and visualize your spending patterns.")

st.subheader("➕ Add New Expense")

with st.form("add_expense_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        expense_date = st.date_input("Date", value=date.today())
    with col2:
        category = st.selectbox("Category", CATEGORIES)

    amount = st.number_input("Amount (₹)", min_value=0.0, step=10.0, format="%.2f")
    description = st.text_input("Description (optional)")

    submitted = st.form_submit_button("Add Expense", use_container_width=True)
    if submitted:
        if amount <= 0:
            st.error("Please enter an amount greater than 0.")
        else:
            add_expense(str(expense_date), category, amount, description)
            st.success(f"Added ₹{amount:.2f} under '{category}'.")
            st.rerun()

df = get_all_expenses()

st.divider()

if df.empty:
    st.info("No expenses recorded yet. Add your first expense above to get started.")
else:
   
    st.subheader("📊 Summary")

    total_spent = df["amount"].sum()
    this_month = df[df["date"].dt.month == date.today().month]
    month_total = this_month["amount"].sum()
    top_category = df.groupby("category")["amount"].sum().idxmax()

    m1, m2, m3 = st.columns(3)
    m1.metric("Total Spent", f"₹{total_spent:,.2f}")
    m2.metric("This Month", f"₹{month_total:,.2f}")
    m3.metric("Top Category", top_category)

    st.divider()

    st.subheader("🔍 Filter Expenses")
    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        selected_categories = st.multiselect(
            "Filter by category", options=CATEGORIES, default=CATEGORIES
        )
    with filter_col2:
        date_range = st.date_input(
            "Date range",
            value=(df["date"].min().date(), df["date"].max().date()),
        )

    filtered_df = df[df["category"].isin(selected_categories)]
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start, end = date_range
        filtered_df = filtered_df[
            (filtered_df["date"].dt.date >= start) & (filtered_df["date"].dt.date <= end)
        ]

    st.divider()

    st.subheader("📈 Visual Insights")

    if filtered_df.empty:
        st.warning("No data matches the selected filters.")
    else:
        tab1, tab2, tab3 = st.tabs(["By Category", "Over Time", "By Day"])

        with tab1:
            category_totals = filtered_df.groupby("category")["amount"].sum().reset_index()
            fig_pie = px.pie(
                category_totals, names="category", values="amount",
                title="Spending Share by Category", hole=0.4
            )
            st.plotly_chart(fig_pie, use_container_width=True)

            fig_bar = px.bar(
                category_totals.sort_values("amount", ascending=True),
                x="amount", y="category", orientation="h",
                title="Total Spending by Category", labels={"amount": "Amount (₹)"}
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        with tab2:
            daily_totals = (
                filtered_df.groupby(filtered_df["date"].dt.date)["amount"]
                .sum()
                .reset_index()
                .rename(columns={"date": "date"})
            )
            fig_line = px.line(
                daily_totals, x="date", y="amount", markers=True,
                title="Spending Trend Over Time", labels={"amount": "Amount (₹)"}
            )
            st.plotly_chart(fig_line, use_container_width=True)

        with tab3:
            filtered_df["weekday"] = filtered_df["date"].dt.day_name()
            weekday_totals = filtered_df.groupby("weekday")["amount"].sum().reindex(
                ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            ).fillna(0).reset_index()
            fig_weekday = px.bar(
                weekday_totals, x="weekday", y="amount",
                title="Spending by Day of Week", labels={"amount": "Amount (₹)"}
            )
            st.plotly_chart(fig_weekday, use_container_width=True)

    st.divider()

    st.subheader("📋 All Records")
    display_df = filtered_df.copy()
    display_df["date"] = display_df["date"].dt.strftime("%Y-%m-%d")
    st.dataframe(
        display_df[["id", "date", "category", "amount", "description"]],
        use_container_width=True,
        hide_index=True,
    )

    with st.expander("🗑️ Delete a record"):
        if not filtered_df.empty:
            ids = filtered_df["id"].tolist()
            id_to_delete = st.selectbox("Select record ID to delete", ids)
            if st.button("Delete Selected Record"):
                delete_expense(id_to_delete)
                st.success(f"Deleted record #{id_to_delete}.")
                st.rerun()

    with st.expander("⚠️ Reset all data"):
        st.warning("This will permanently delete all recorded expenses.")
        if st.button("Clear All Expenses", type="secondary"):
            clear_all_expenses()
            st.success("All expenses cleared.")
            st.rerun()
