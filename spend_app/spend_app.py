# impot the library needed
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import os
import numpy as np
from datetime import date, datetime
from datetime import date, timedelta
from numpy.random import default_rng as rng

# add the sidbar with pages 
with st.sidebar:
    page_chosen = st.radio(
        "MENU",
        ("Dashboard", "Add Book", "Check-in / Check-out", "Search Catalog", "View Inventory")
    )

# Setting up the dashboard page
if page_chosen == "Dashboard":
    
    st.title("Dashboard")
    st.header(":red[_LIBRARY SYSTEM_] :material/book:")
    st.text("Book & Member Management Platform")
    st.header(":red[_Welcome to GA Library Dashboard_] :material/book:")
    st.text("Manage books, track lending and explore library insights.")

    books = pd.read_csv("library_books.csv", dtype=str)

    # Books Statistics
  
    st.subheader("Library Statistics")

    books["Status"] = books["Status"].fillna("").str.strip()
    books["Expected Return Date"] = books["Expected Return Date"].fillna("").str.strip()
    
    available = (books["Status"] == "Available").sum()
    borrowed = (books["Status"] == "Borrowed").sum()
    
    expected_dates = pd.to_datetime(
        books["Expected Return Date"],
        errors="coerce"
    )
    
    today = pd.Timestamp.today().normalize()
    
    overdue = (
        (books["Status"] == "Borrowed") &
        (expected_dates < today)
    ).sum()


    a, b = st.columns(2)
    c, d = st.columns(2)
    
    a.metric("Total Books", len(books))
    b.metric("Available", available)
    c.metric("Borrowed", borrowed)
    d.metric("Overdue", overdue)

    # Overdue Alert
    st.subheader("Overdue Alert")
    
    books = pd.read_csv("library_books.csv", dtype=str)
    
    books["Status"] = books["Status"].fillna("").str.strip()
    books["Expected Return Date"] = books["Expected Return Date"].fillna("").str.strip()
    books["Actual Return Date"] = books["Actual Return Date"].fillna("").str.strip()
    
    today = pd.Timestamp.today().normalize()
    
    expected_dates = pd.to_datetime(
        books["Expected Return Date"],
        errors="coerce"
    )
    
    late = books[
        (books["Status"] == "Borrowed") &
        (expected_dates < today) &
        (books["Actual Return Date"] == "")
    ]
    
    if late.empty:
        st.success("No overdue books!")
    else:
        st.warning("The following books are overdue:")
        st.dataframe(late, hide_index=True)

    # Books by Categories chart
    st.subheader("Books by Categories")

    source = pd.read_csv("library_books.csv")
    
    category_count = source["Book Categories"].value_counts().reset_index()
    
    category_count.columns = ["Book Categories", "Number of Books"]
    
    st.bar_chart(category_count, x="Book Categories", y="Number of Books", color="#4A90A4")

    
    st.divider()
    
    # Book Types Distribution chart
    st.subheader("Book Types Distribution")

    books = pd.read_csv("library_books.csv")

    book_types = books["Book type"].value_counts()
        
    st.bar_chart(book_types, color="#4A90A4")

    
    st.divider()

    # Book Availability line
    available = (books["Status"] == "Available").sum()
    checked_out = (books["Status"] == "Borrowed").sum()
    
    total = available + checked_out
    
    st.subheader("Book Availability")
    
    st.progress(available / total if total > 0 else 0)
    
    st.caption(f"Available: {available} | Borrowed: {checked_out}")


# Setting up the add book page
if page_chosen == "Add Book":
    st.title("Add Book")
    
    st.header("_Book_  :orange[Details] :material/book:")
    
    title = st.text_input("Title")

    col1, col2 = st.columns(2)

    with col1:
        id = st.number_input("ID", step=1)
    
    with col2:
        author = st.text_input("Author","")


    categories = st.radio("Book Categories",
    ["Fiction", "Science", "Technology", "Business", "History", "Education", "Psychology", "Self-Development"],
    index=None, horizontal = True)

    st.write("Book Categories:", categories)

    option = st.selectbox(
    "Book type",
    ("Paperback", "E-book", "Hardcover"))
    
    st.write("You selected:", option)
    
    # Add Book button
    if st.button("Add Book"):
        st.write("Done")
        
        new_row=pd.DataFrame({"ID":[id],"Title":[title], "Author":[author], "Book Categories":[categories], "Book type":[option]})
        
        df = pd.read_csv("library_books.csv")
    
        # Check if ID already exists
        if id in df["ID"].values:
            st.error("This Book ID already exists! Please use another ID.")
    
        else:
            new_df = pd.concat([df, new_row], ignore_index=True)
    
            new_df.to_csv("library_books.csv", index=False)
    
            st.success("Book added successfully!")
            st.dataframe(new_df)

# Setting up the Check-in / Check-out page
if page_chosen == "Check-in / Check-out":
    st.title("Check-in / Check-out")
    
    # Check-in (Borrow Book)
    st.header(":orange[_Check-in_]")
    
    col1, col2 = st.columns(2)

    with col1:
        id = st.number_input("ID", step=1)
    
    with col2:
        title = st.text_input("Title","")

    col3, col4 = st.columns(2)

    with col3:
        borrow_date = st.date_input("Borrow Date (_Today_)", value=None)
        st.write("Borrow Date:", borrow_date)
    
    with col4:
        expected_return_date = st.date_input("Expected Return Date", value=None, max_value=date.today() + timedelta(days=14))

    st.write("Expected Return Date:", expected_return_date)

    books = pd.read_csv("library_books.csv", dtype=str)
    
    if "Status" not in books.columns:
        books["Status"] = "Available"
    
    if "Borrow Date" not in books.columns:
        books["Borrow Date"] = ""
    
    if "Expected Return Date" not in books.columns:
        books["Expected Return Date"] = ""
    
    if "Actual Return Date" not in books.columns:
        books["Actual Return Date"] = ""
    
    books["Borrow Date"] = books["Borrow Date"].fillna("").astype(str)
    books["Expected Return Date"] = books["Expected Return Date"].fillna("").astype(str)
    books["Actual Return Date"] = books["Actual Return Date"].fillna("").astype(str)
    
    books.to_csv("library_books.csv", index=False)

    if st.button("Borrow Book"):

        book = books[books["ID"] == str(id)]

        if book.empty:
            st.error("Book Not Found!")

        elif book.iloc[0]["Status"] == "Borrowed":
            st.error("Book is already borrowed!")

        elif borrow_date >= expected_return_date:
            st.error("Invalid Dates!")

        else:
            books.loc[book.index, "Status"] = "Borrowed"
            books.loc[book.index, "Borrow Date"] = str(borrow_date)
            books.loc[book.index, "Expected Return Date"] = str(expected_return_date)
            books.loc[book.index, "Actual Return Date"] = ""

            books.to_csv("library_books.csv", index=False)

            st.success("Book Borrowed Successfully!")

    # Check-out (Return Book)
    st.divider()

    st.header(":green[_Check-out_]")

    checkout_id = st.number_input("Book ID to Return",min_value=0,step=1,key="checkout_id")

    if st.button("Return Book"):

        book = books[books["ID"] == str(checkout_id)]

        if book.empty:
            st.error("Book Not Found!")

        elif book.iloc[0]["Status"] == "Available":
            st.warning("Book is already available!")

        else:
            books.loc[book.index, "Status"] = "Available"
            books.loc[book.index, "Actual Return Date"] = str(date.today())

            books.to_csv("library_books.csv", index=False)

            st.success("Book Returned Successfully!")
    
# Setting up the Search Catalog page
if page_chosen == "Search Catalog":

    st.header(":red[_You're in the library. Enjoy — no ads, just books!_]")
    st.header("📚 Browse our book collection and discover your next favorite read.")

    books = pd.read_csv("library_books.csv")
    st.title("Search Book")
   
    search = st.text_input("Write the Book Title or ID or Auther Name")
    
    if search:
        result = books[
            books["Title"].str.contains(search, case=False, na=False) |
            books["ID"].astype(str).str.contains(search, case=False, na=False) |
            books["Author"].str.contains(search, case=False, na=False)
        ]
    
        st.dataframe(result)

    # Random Book Generator    
    st.subheader("Random Book Generator")
    
    if st.button("Suggest a Book"):
        suggested_book = books.sample(1).iloc[0]
    
        st.success("Here is your suggested book!")
    
        st.write("**ID:**", suggested_book["ID"])
        st.write("**Title:**", suggested_book["Title"])
        st.write("**Author:**", suggested_book["Author"])
        st.write("**Category:**", suggested_book["Book Categories"])
        st.write("**Book Type:**", suggested_book["Book type"])
    
# Setting up the Search View Inventory page
if page_chosen == "View Inventory":
    st.title("View Inventory")
    st.header(":orange[Library Collection]")

    books = pd.read_csv("library_books.csv")
        
    st.dataframe(books, hide_index=True, width="stretch", height="content")

    # Upload CSV
    uploaded_file = st.file_uploader(
        "Upload Library CSV",
        type=["csv"]
    )
    
    if uploaded_file is not None:
    
        if st.button("Load Data"):
    
            books = pd.read_csv(uploaded_file, dtype=str)
    
            books.to_csv("library_books.csv", index=False)
    
            st.success("Data Uploaded Successfully!")
    
            st.rerun()
            
    # Download CSV
    st.download_button(
        "Download Library CSV",
        data=books.to_csv(index=False).encode("utf-8"),
        file_name="library_books.csv",
        mime="text/csv"
    )

# Add footer 
from datetime import date

st.divider()

st.caption(
    f"Library System | {date.today().strftime('%d %B %Y')}"
)

st.caption("Done by: Almeqdad Matar")
st.caption("instructors: Jamila & Abdulrahman")
st.caption("GA Data Science Bootcamp")

