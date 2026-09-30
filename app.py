import streamlit as st
import json
import os
from datetime import date
import pandas as pd
import plotly.express as px

DATA_FILE = "attendance_data.json"

st.set_page_config(
    page_title="Student Attendance Tracker",
    page_icon="📚",
    layout="wide"
)

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as file:
                return json.load(file)
        except:
            return {"students": [], "attendance": {}}
    return {"students": [], "attendance": {}}

def save_data():
    with open(DATA_FILE, "w") as file:
        json.dump(st.session_state.data, file, indent=4)

if "data" not in st.session_state:
    st.session_state.data = load_data()

if "edit_student" not in st.session_state:
    st.session_state.edit_student = None

students = st.session_state.data["students"]
attendance = st.session_state.data["attendance"]

st.markdown(
    """
    <style>
    .main-title {
        font-size: 38px;
        font-weight: 700;
        text-align: center;
        margin-bottom: 5px;
    }

    .sub-title {
        text-align: center;
        font-size: 17px;
        color: #666;
        margin-bottom: 25px;
    }

    .metric-card {
        padding: 15px;
        border-radius: 12px;
        background-color: #f7f9fc;
        text-align: center;
    }

    div.stButton > button {
        border-radius: 8px;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    '<div class="main-title">📚 Student Attendance Tracker</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">Manage students, record attendance and monitor attendance performance</div>',
    unsafe_allow_html=True
)

menu = st.sidebar.radio(
    "📌 Navigation",
    [
        "🏠 Dashboard",
        "➕ Add Student",
        "👥 View Students",
        "✏️ Edit Student",
        "🗑️ Delete Student",
        "📝 Mark Attendance",
        "📊 View Attendance",
        "📈 Attendance Percentage",
        "📋 Attendance Summary",
        "📉 Charts"
    ]
)

total_students = len(students)

total_records = sum(
    len(records) for records in attendance.values()
)

present_records = sum(
    sum(1 for record in records if record["status"] == "Present")
    for records in attendance.values()
)

overall_percentage = (
    (present_records / total_records) * 100
    if total_records > 0 else 0
)

if menu == "🏠 Dashboard":

    st.subheader("📊 Dashboard")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("👥 Total Students", total_students)
    col2.metric("📝 Attendance Records", total_records)
    col3.metric("✅ Present", present_records)
    col4.metric("📈 Overall Attendance", f"{overall_percentage:.1f}%")

    st.divider()

    if students:
        data = []

        for student in students:
            student_id = student["id"]
            records = attendance.get(student_id, [])

            total = len(records)
            present = sum(
                1 for record in records
                if record["status"] == "Present"
            )

            percentage = (present / total * 100) if total else 0

            data.append({
                "ID": student["id"],
                "Name": student["name"],
                "Course": student["course"],
                "Year": student["year"],
                "Attendance": f"{percentage:.1f}%"
            })

        df = pd.DataFrame(data)

        st.subheader("👥 Student Attendance Overview")
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("No students added yet. Use 'Add Student' to begin.")

elif menu == "➕ Add Student":

    st.subheader("➕ Add Student")

    with st.form("add_student_form"):

        col1, col2 = st.columns(2)

        with col1:
            student_id = st.text_input("Student ID")
            name = st.text_input("Student Name")

        with col2:
            course = st.text_input("Course")
            year = st.selectbox(
                "Year",
                ["1st Year", "2nd Year", "3rd Year", "4th Year"]
            )

        submitted = st.form_submit_button(
            "➕ Add Student",
            use_container_width=True
        )

        if submitted:

            student_id = student_id.strip()
            name = name.strip()
            course = course.strip()

            if not student_id or not name or not course:
                st.error("Please fill all required fields.")

            elif any(
                student["id"] == student_id
                for student in students
            ):
                st.error("Student ID already exists.")

            else:
                students.append({
                    "id": student_id,
                    "name": name,
                    "course": course,
                    "year": year
                })

                attendance[student_id] = []

                save_data()

                st.success("Student added successfully!")
                st.rerun()

elif menu == "👥 View Students":

    st.subheader("👥 View Students")

    if students:

        df = pd.DataFrame(students)

        df.columns = [
            "Student ID",
            "Name",
            "Course",
            "Year"
        ]

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("No students available.")

elif menu == "✏️ Edit Student":

    st.subheader("✏️ Edit Student")

    if not students:
        st.info("No students available.")
    else:

        student_ids = [student["id"] for student in students]

        selected_id = st.selectbox(
            "Select Student",
            student_ids
        )

        selected_student = next(
            student for student in students
            if student["id"] == selected_id
        )

        with st.form("edit_student_form"):

            name = st.text_input(
                "Student Name",
                value=selected_student["name"]
            )

            course = st.text_input(
                "Course",
                value=selected_student["course"]
            )

            year = st.selectbox(
                "Year",
                ["1st Year", "2nd Year", "3rd Year", "4th Year"],
                index=[
                    "1st Year",
                    "2nd Year",
                    "3rd Year",
                    "4th Year"
                ].index(selected_student["year"])
            )

            submitted = st.form_submit_button(
                "💾 Update Student",
                use_container_width=True
            )

            if submitted:

                if not name.strip() or not course.strip():
                    st.error("Name and course cannot be empty.")
                else:

                    selected_student["name"] = name.strip()
                    selected_student["course"] = course.strip()
                    selected_student["year"] = year

                    save_data()

                    st.success("Student details updated successfully!")
                    st.rerun()

elif menu == "🗑️ Delete Student":

    st.subheader("🗑️ Delete Student")

    if not students:
        st.info("No students available.")
    else:

        student_ids = [student["id"] for student in students]

        selected_id = st.selectbox(
            "Select Student to Delete",
            student_ids
        )

        selected_student = next(
            student for student in students
            if student["id"] == selected_id
        )

        st.warning(
            f"You are about to delete {selected_student['name']}."
        )

        confirm = st.checkbox(
            "I confirm that I want to delete this student."
        )

        if st.button(
            "🗑️ Delete Student",
            use_container_width=True
        ):

            if not confirm:
                st.error("Please confirm deletion first.")
            else:

                st.session_state.data["students"] = [
                    student for student in students
                    if student["id"] != selected_id
                ]

                if selected_id in attendance:
                    del attendance[selected_id]

                save_data()

                st.success("Student deleted successfully!")
                st.rerun()

elif menu == "📝 Mark Attendance":

    st.subheader("📝 Mark Attendance")

    if not students:
        st.info("Add students before marking attendance.")
    else:

        attendance_date = st.date_input(
            "📅 Attendance Date",
            value=date.today()
        )

        st.divider()

        attendance_options = {}

        for student in students:

            col1, col2, col3 = st.columns([2, 2, 1])

            with col1:
                st.write(
                    f"**{student['id']} - {student['name']}**"
                )

            with col2:
                st.write(
                    f"{student['course']} | {student['year']}"
                )

            with col3:
                attendance_options[student["id"]] = st.selectbox(
                    "Status",
                    ["Present", "Absent"],
                    key=f"status_{student['id']}"
                )

        st.divider()

        if st.button(
            "💾 Save Attendance",
            use_container_width=True
        ):

            formatted_date = attendance_date.isoformat()

            for student_id, status in attendance_options.items():

                records = attendance.setdefault(
                    student_id,
                    []
                )

                existing_record = next(
                    (
                        record
                        for record in records
                        if record["date"] == formatted_date
                    ),
                    None
                )

                if existing_record:
                    existing_record["status"] = status
                else:
                    records.append({
                        "date": formatted_date,
                        "status": status
                    })

            save_data()

            st.success("Attendance saved successfully!")

elif menu == "📊 View Attendance":

    st.subheader("📊 View Attendance")

    if not students:
        st.info("No students available.")
    else:

        selected_id = st.selectbox(
            "Select Student",
            [student["id"] for student in students]
        )

        selected_student = next(
            student for student in students
            if student["id"] == selected_id
        )

        records = attendance.get(selected_id, [])

        st.write(
            f"### {selected_student['name']} ({selected_id})"
        )

        if records:

            df = pd.DataFrame(records)

            df["Date"] = pd.to_datetime(
                df["date"]
            ).dt.strftime("%d-%m-%Y")

            df = df[["Date", "status"]]

            df.columns = ["Date", "Status"]

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

        else:
            st.info("No attendance records found.")

elif menu == "📈 Attendance Percentage":

    st.subheader("📈 Attendance Percentage")

    if not students:
        st.info("No students available.")
    else:

        selected_id = st.selectbox(
            "Select Student",
            [student["id"] for student in students]
        )

        selected_student = next(
            student for student in students
            if student["id"] == selected_id
        )

        records = attendance.get(selected_id, [])

        total = len(records)

        present = sum(
            1 for record in records
            if record["status"] == "Present"
        )

        absent = total - present

        percentage = (
            present / total * 100
            if total > 0 else 0
        )

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Classes", total)
        col2.metric("Present", present)
        col3.metric(
            "Attendance Percentage",
            f"{percentage:.2f}%"
        )

        st.progress(
            min(percentage / 100, 1.0)
        )

        if percentage >= 75:
            st.success(
                f"{selected_student['name']} has {percentage:.2f}% attendance."
            )
        else:
            st.warning(
                f"{selected_student['name']} has {percentage:.2f}% attendance."
            )

elif menu == "📋 Attendance Summary":

    st.subheader("📋 Attendance Summary")

    if not students:
        st.info("No students available.")
    else:

        summary = []

        for student in students:

            records = attendance.get(
                student["id"],
                []
            )

            total = len(records)

            present = sum(
                1
                for record in records
                if record["status"] == "Present"
            )

            absent = total - present

            percentage = (
                present / total * 100
                if total > 0 else 0
            )

            summary.append({
                "Student ID": student["id"],
                "Name": student["name"],
                "Course": student["course"],
                "Total Classes": total,
                "Present": present,
                "Absent": absent,
                "Attendance %": round(
                    percentage,
                    2
                )
            })

        df = pd.DataFrame(summary)

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

elif menu == "📉 Charts":

    st.subheader("📉 Attendance Charts")

    if not students:
        st.info("No students available.")
    else:

        chart_data = []

        for student in students:

            records = attendance.get(
                student["id"],
                []
            )

            total = len(records)

            present = sum(
                1
                for record in records
                if record["status"] == "Present"
            )

            percentage = (
                present / total * 100
                if total > 0 else 0
            )

            chart_data.append({
                "Student": student["name"],
                "Attendance": round(
                    percentage,
                    2
                )
            })

        df = pd.DataFrame(chart_data)

        fig = px.bar(
            df,
            x="Student",
            y="Attendance",
            title="Student Attendance Percentage",
            text="Attendance",
            range_y=[0, 100]
        )

        fig.update_traces(
            texttemplate="%{text}%",
            textposition="outside"
        )

        fig.update_layout(
            yaxis_title="Attendance Percentage (%)",
            xaxis_title="Student",
            height=500
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        total_present = sum(
            sum(
                1
                for record in attendance.get(
                    student["id"],
                    []
                )
                if record["status"] == "Present"
            )
            for student in students
        )

        total_absent = sum(
            sum(
                1
                for record in attendance.get(
                    student["id"],
                    []
                )
                if record["status"] == "Absent"
            )
            for student in students
        )

        status_df = pd.DataFrame({
            "Status": ["Present", "Absent"],
            "Count": [
                total_present,
                total_absent
            ]
        })

        fig2 = px.pie(
            status_df,
            names="Status",
            values="Count",
            title="Overall Attendance Distribution"
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

st.sidebar.divider()

st.sidebar.caption(
    "📚 Student Attendance Tracker"
)

st.sidebar.caption(
    "Built with Python & Streamlit"
)