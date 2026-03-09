import streamlit as st
import pandas as pd
import json
import os
import plotly.express as px

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Student Dashboard", layout="wide")

DATA_FILE = "students.json"


# ---------------- LOAD DATA ----------------
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []


# ---------------- SAVE DATA ----------------
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


# ---------------- GRADE FUNCTION ----------------
def calculate_grade(avg):
    if avg >= 90:
        return "A"
    elif avg >= 75:
        return "B"
    elif avg >= 60:
        return "C"
    elif avg >= 50:
        return "D"
    else:
        return "F"


students = load_data()

# ---------------- LOGIN SYSTEM ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


def login():
    st.title("🔐 Student Dashboard Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "admin" and password == "1234":
            st.session_state.logged_in = True
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Invalid credentials")


if not st.session_state.logged_in:
    login()
    st.stop()


# ---------------- THEME SWITCH ----------------
theme = st.sidebar.radio("Theme", ["Dark", "Light"])

if theme == "Dark":
    st.markdown("""
    <style>
    .stApp {background-color:#0f172a; color:white;}
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
    .stApp {background-color:white; color:black;}
    </style>
    """, unsafe_allow_html=True)


# ---------------- SIDEBAR MENU ----------------
menu = st.sidebar.selectbox(
    "Navigation",
    [
        "Dashboard",
        "Add Student",
        "View Students",
        "Search Student",
        "Update Marks",
        "Delete Student",
        "Leaderboard",
        "Analytics",
        "Upload Excel"
    ]
)

st.title("📊 Student Record Management Dashboard")


# ---------------- DASHBOARD ----------------
if menu == "Dashboard":

    if students:

        df = pd.DataFrame(students)

        col1, col2, col3 = st.columns(3)

        col1.metric("🎓 Total Students", len(df))
        col2.metric("📊 Class Average", round(df["average"].mean(), 2))
        col3.metric("🏆 Highest Score", df["total"].max())

        fig = px.histogram(df, x="grade", title="Grade Distribution")
        st.plotly_chart(fig)

    else:
        st.info("No student records available")


# ---------------- ADD STUDENT ----------------
elif menu == "Add Student":

    st.subheader("➕ Add New Student")

    name = st.text_input("Student Name")
    roll = st.text_input("Roll Number")

    marks = []
    for i in range(1, 6):
        marks.append(st.number_input(f"Subject {i} Marks", 0, 100))

    if st.button("Add Student"):

        for s in students:
            if s["roll"] == roll:
                st.error("Roll number already exists")
                st.stop()

        total = sum(marks)
        avg = total / 5

        student = {
            "name": name,
            "roll": roll,
            "marks": marks,
            "total": total,
            "average": avg,
            "grade": calculate_grade(avg)
        }

        students.append(student)
        save_data(students)

        st.success("Student added successfully")


# ---------------- VIEW STUDENTS ----------------
elif menu == "View Students":

    st.subheader("📋 All Student Records")

    if students:
        df = pd.DataFrame(students)

        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False).encode('utf-8')

        st.download_button(
            "📥 Download CSV",
            csv,
            "students.csv",
            "text/csv"
        )

    else:
        st.warning("No student records found")


# ---------------- SEARCH STUDENT ----------------
elif menu == "Search Student":

    st.subheader("🔍 Search Student")

    roll = st.text_input("Enter Roll Number")

    found = False

    for s in students:
        if s["roll"] == roll:
            st.success("Student Found")
            st.write(s)
            found = True

    if roll and not found:
        st.error("Student not found")


# ---------------- UPDATE MARKS ----------------
elif menu == "Update Marks":

    st.subheader("✏ Update Student Marks")

    roll = st.text_input("Enter Roll Number")

    for s in students:

        if s["roll"] == roll:

            new_marks = []

            for i in range(1, 6):
                new_marks.append(st.number_input(f"Subject {i}", 0, 100))

            if st.button("Update Marks"):

                s["marks"] = new_marks
                s["total"] = sum(new_marks)
                s["average"] = s["total"] / 5
                s["grade"] = calculate_grade(s["average"])

                save_data(students)

                st.success("Marks updated successfully")

            break


# ---------------- DELETE STUDENT ----------------
elif menu == "Delete Student":

    st.subheader("🗑 Delete Student")

    roll = st.text_input("Enter Roll Number")

    if st.button("Delete"):

        new_students = [s for s in students if s["roll"] != roll]

        save_data(new_students)

        st.success("Student deleted")


# ---------------- LEADERBOARD ----------------
elif menu == "Leaderboard":

    st.subheader("🏆 Top Students")

    if students:

        df = pd.DataFrame(students)

        top_students = df.sort_values(by="total", ascending=False).head(5)

        st.table(top_students[["name", "roll", "total", "grade"]])

    else:
        st.info("No data available")


# ---------------- ANALYTICS ----------------
elif menu == "Analytics":

    st.subheader("📊 Student Performance Analytics")

    if students:

        df = pd.DataFrame(students)

        fig = px.bar(
            df,
            x="name",
            y="total",
            color="grade",
            title="Student Total Marks"
        )

        st.plotly_chart(fig)

        fig2 = px.line(
            df,
            x="name",
            y="average",
            title="Average Marks Trend"
        )

        st.plotly_chart(fig2)

    else:
        st.warning("No analytics data available")


# ---------------- EXCEL UPLOAD ----------------
elif menu == "Upload Excel":

    st.subheader("📂 Upload Student Data from Excel")

    uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

    if uploaded_file:

        excel_data = pd.read_excel(uploaded_file)

        st.write("Preview Data")
        st.dataframe(excel_data)

        if st.button("Import Data"):

            students.extend(excel_data.to_dict("records"))

            save_data(students)

            st.success("Data imported successfully")