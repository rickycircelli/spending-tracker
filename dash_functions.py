import json
import pandas as pd
import os
from glob import glob
import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime, timedelta


def read_data():
    folder = "data"

    def get_latest_csv(prefix):
        files = glob(os.path.join(folder, f"{prefix}_*.csv"))
        if not files:
            print(f"No files found for prefix: {prefix}")
            return None
        files.sort(reverse=True) # sort by date and prefix escending
        return pd.read_csv(files[0]) 

    df_accounts = get_latest_csv("accounts")
    df_checking = get_latest_csv("checking_transactions")
    df_credit = get_latest_csv("credit_transactions")

    return df_accounts, df_checking, df_credit

# credit vs checking
def credit_checking():
    df_accounts, _, _= read_data()
    
     # error check
    if df_accounts is None:
        st.warning("No accounts data found.")
        return
    
    credit = df_accounts[df_accounts["subtype"] == "credit card"]["balance"].sum()
    checking = df_accounts[df_accounts["subtype"] == "checking"]["balance"].sum()
    difference = checking - credit

    st.metric("Checking Balance", f"${checking:,.2f}")
    st.metric("Credit Card Balance", f"${credit:,.2f}")
    st.success(f"**Difference: ${difference:,.2f}**")

    # warning if checking is low
    if difference < 150:
        st.error("⚠️ Your checking balance is getting close to your credit balance. Consider adding funds.")


#net worth
def net_worth():
    df_accounts, _, _ = read_data()

    # error check
    if df_accounts is None:
        st.warning("No accounts data found.")
        return

    savings = df_accounts[df_accounts["subtype"] == "savings"]["balance"].sum()
    credit = df_accounts[df_accounts["subtype"] == "credit card"]["balance"].sum()
    checking = df_accounts[df_accounts["subtype"] == "checking"]["balance"].sum()

    net_worth = savings + checking - credit
    st.metric("Savings", f"${savings:,.2f}")
    st.metric("Checking", f"${checking:,.2f}")
    st.metric("Credit Owed", f"-${credit:,.2f}")
    st.success(f"**Net Worth: ${net_worth:,.2f}**")

# spedning per month
def spending_per_month():
    _, _, df_credit = read_data()

    # error check
    if df_credit is None or df_credit.empty:
        st.warning("No credit card transaction data found.")
        return
    
    # datetime format
    df_credit["date"] = pd.to_datetime(df_credit["date"])

    # filter for only (+) amounts 
    df_credit = df_credit[df_credit["amount"] > 0]

    # convert to positive for spending (safegaurd)
    df_credit["spending"] = df_credit["amount"].abs()

    # format month
    df_credit["month"] = df_credit["date"].dt.strftime("%b %Y")

    # group by month
    monthly_spend = df_credit.groupby("month")["spending"].sum().reset_index()

    # plot
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(monthly_spend["month"], monthly_spend["spending"], color="#007BFF")

    # spending labels on top of bars
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f"${height:,.0f}",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 5),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=10)

    ax.set_ylabel("Amount ($)")
    
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)

    ax.set_xlabel("Month")
    plt.xticks()
    plt.tight_layout()

    st.pyplot(fig)

#spending per category (last 30 days)
def spending_per_cat():
    _, _, df_credit = read_data()

    # error check
    if df_credit is None:
        st.warning("No credit card data found.")
        return

    # datetime and filter last 30 days
    df_credit["date"] = pd.to_datetime(df_credit["date"])
    last_30 = df_credit[df_credit["date"] >= datetime.today() - timedelta(days=30)]

    # keep only (+) amounts 
    last_30 = last_30[last_30["amount"] > 0].copy()

    # parse category string (assumes format like "['Shopping', 'Clothing']")
    last_30["category"] = last_30["category"].apply(
        lambda x: eval(x)[0] if pd.notnull(x) and len(eval(x)) > 0 else "Uncategorized"
    )

    # group by category and sum
    category_spend = last_30.groupby("category")["amount"].sum()
    category_spend = category_spend.sort_values()

    # error check
    if category_spend.empty:
        st.info("No credit card transactions in the last 30 days.")
        return

    # plot 
    fig, ax = plt.subplots(figsize=(10, 6))

    bars = ax.barh(category_spend.index, category_spend.values, color="#FF5733")
    ax.set_xlabel("Amount ($)")

    # labels 
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 5, bar.get_y() + bar.get_height()/2, f"${width:,.0f}",
                va='center', fontsize=9)

    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)

    plt.tight_layout()
    st.pyplot(fig)

#spending per category pie (last 30 days)
def spending_per_cat_pie():
    _, _, df_credit = read_data()

    if df_credit is None:
        st.warning("Credit transaction data not available.")
        return

    # datetime and filter last 30 days
    df_credit["date"] = pd.to_datetime(df_credit["date"])
    last_30 = df_credit[df_credit["date"] >= datetime.today() - timedelta(days=30)]

    # keep only (+) amounts 
    last_30 = last_30[last_30["amount"] > 0].copy()

    # parse category string (assumes format like "['Shopping', 'Clothing']")
    last_30["category"] = last_30["category"].apply(
        lambda x: eval(x)[0] if pd.notnull(x) and len(eval(x)) > 0 else "Uncategorized"
    )

    # group by category and sum
    spending = last_30.groupby("category")["amount"].sum()

    if spending.empty:
        st.info("No spending activity in the last 30 days.")
        return

    # plot
    fig, ax = plt.subplots()
    ax.pie(spending, labels=spending.index, autopct="%1.1f%%", startangle=90)
    ax.axis("equal")
    st.pyplot(fig)


# income vs expenses
def income_expenses():
    _, df_checking, df_credit = read_data()

    if df_checking is None or df_credit is None:
        st.warning("Transaction data not available.")
        return

    df_checking["date"] = pd.to_datetime(df_checking["date"])
    df_credit["date"] = pd.to_datetime(df_credit["date"])
    
    # Categorize transactions
    df_income = df_checking[df_checking["amount"] < 0]
    df_expenses = df_credit[df_credit["amount"] > 0]

    # Add "year-month" column
    df_income["month"] = df_income["date"].dt.to_period("M")
    df_expenses["month"] = df_expenses["date"].dt.to_period("M")

    # Group by month and sum amounts
    income_by_month = df_income.groupby("month")["amount"].sum().abs()  # abs() to make positive
    expense_by_month = df_expenses.groupby("month")["amount"].sum()

    # Align indexes
    all_months = income_by_month.index.union(expense_by_month.index).sort_values()
    income_by_month = income_by_month.reindex(all_months, fill_value=0)
    expense_by_month = expense_by_month.reindex(all_months, fill_value=0)

    # Plot
    fig, ax = plt.subplots(figsize=(10, 6))
    labels = all_months.to_timestamp().strftime("%b %Y")
    bar1 = ax.bar(labels, income_by_month, label="Income", color = "green")
    bar2 = ax.bar(labels, expense_by_month, label="Expenses", color = "red", alpha=0.7)

    # Add values on top of each bar
    for bars in [bar1, bar2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2, 
                height + 5, 
                f"${height:,.0f}", 
                ha="center", 
                va="bottom",
                fontsize=8
            )

    ax.set_ylabel("Amount ($)")
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.legend()
    plt.xticks()
    st.pyplot(fig)


# recurrring transactions
def supscriptions():
    _, df_checking, df_credit = read_data()

    if df_checking is None or df_credit is None:
        st.warning("Transaction data not available.")
        return
    
    # ignore refunds/payments
    df_credit_checking = pd.concat([df_credit, df_checking], ignore_index=True)
    df_credit_checking = df_credit_checking[df_credit_checking["amount"] > 0]  
    df_credit_checking["date"] = pd.to_datetime(df_credit_checking["date"])
    df_credit_checking["year_month"] = df_credit_checking["date"].dt.to_period("M")

    # exclude merchants with more than 1 charge in the same month
    month_counts = df_credit_checking.groupby(["merchant_name", "year_month"]).size().reset_index(name="count")
    bad_merchants = month_counts[month_counts["count"] > 1]["merchant_name"].unique()
    df_credit_checking = df_credit_checking[~df_credit_checking["merchant_name"].isin(bad_merchants)]

    # group by merchant name
    grouped = df_credit_checking.groupby("merchant_name")

    possible_subs = []

    for merchant_name, group in grouped:
        # check how many transactions
        if len(group) < 2:
            continue  

        group = group.sort_values("date")
        group["day_diff"] = group["date"].diff().dt.days
        group["amount_diff"] = group["amount"].diff().abs()

        # check for monthly interval and similar price
        monthly_count = ((group["day_diff"] > 25) & (group["day_diff"] < 35)).sum()
        consistent_price = (group["amount_diff"] <= 2).sum()

        if monthly_count >= 1 and consistent_price >= 1:
            possible_subs.append({
                "merchant_name": merchant_name,
                "avg_amount": round(group["amount"].mean(), 2),
                "count": len(group)
            })
    
    # display 
    subs_df = pd.DataFrame(possible_subs)
    st.dataframe(subs_df)

def spending_per_merchant():
    _, _, df_credit = read_data()

    # error check
    if df_credit is None:
        st.warning("No credit card data found.")
        return

    # datetime and filter last 30 days
    df_credit["date"] = pd.to_datetime(df_credit["date"])
    last_30 = df_credit[df_credit["date"] >= datetime.today() - timedelta(days=30)]

    # keep only (+) amounts 
    last_30 = last_30[last_30["amount"] > 0].copy()

    # group by merchant_name and sum
    merchant_spend = last_30.groupby("merchant_name")["amount"].sum()
    merchant_spend = merchant_spend.sort_values()

    # error check
    if merchant_spend.empty:
        st.info("No credit card transactions in the last 30 days.")
        return

    # plot 
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(merchant_spend.index, merchant_spend.values, color="#FF5733")
    ax.set_xlabel("Amount ($)")

    # labels 
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 5, bar.get_y() + bar.get_height()/2, f"${width:,.0f}",
                va='center', fontsize=9)

    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)

    plt.tight_layout()
    st.pyplot(fig)

if __name__ == "__main__":
    read_data()

