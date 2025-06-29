import streamlit as st
import pandas as pd

# ---- Load Data from CSV ----
@st.cache_data
def load_courses_from_csv(csv_path):
    df = pd.read_csv(csv_path)
    df.columns = [col.strip() for col in df.columns]
    df["Course Code"] = df["Course Code"].astype(str)
    df["Title"] = df["Title"].astype(str)
    return df

csv_path = "CLASS-ROUTINE-252_cleaned.csv"
courses_df = load_courses_from_csv(csv_path)

st.title("📚 UIU Course Selector - Summer 2025")

if "selected_courses" not in st.session_state:
    st.session_state.selected_courses = pd.DataFrame(columns=courses_df.columns)

search_term = st.text_input("🔍 Search course by code or title").strip()

if search_term:
    filtered_df = courses_df[
        courses_df["Course Code"].str.contains(search_term, case=False, na=False) |
        courses_df["Title"].str.contains(search_term, case=False, na=False)
    ]

    st.subheader("📌 Search Results")

    if filtered_df.empty:
        st.info("No courses found matching your search.")
    else:
        display_cols = ["Course Code", "Title", "Section", "Day1", "Time1", "Day2", "Time2", "Room1", "Room2", "Faculty Name", "Credit"]
        st.dataframe(filtered_df[display_cols].reset_index(drop=True))

        st.markdown("---")
        st.write("**Add courses:**")
        for idx, row in filtered_df.iterrows():
            cols = st.columns([8, 1])
            with cols[0]:
                st.write(f"{row['Course Code']} - {row['Title']} ({row['Section']})")
            with cols[1]:
                if st.button("➕ Add", key=f"add_{idx}"):
                    already_added = (
                        (st.session_state.selected_courses["Course Code"] == row["Course Code"]) &
                        (st.session_state.selected_courses["Section"] == row["Section"])
                    ).any()
                    if not already_added:
                        st.session_state.selected_courses = pd.concat(
                            [st.session_state.selected_courses, pd.DataFrame([row])],
                            ignore_index=True
                        )
                        st.success(f"✅ Added {row['Course Code']} - {row['Section']}")
                    else:
                        st.warning(f"⚠️ {row['Course Code']} - {row['Section']} is already added.")

st.subheader("📋 Selected Courses")

if st.session_state.selected_courses.empty:
    st.info("No courses added yet.")
else:
    selected_display_cols = ["Course Code", "Title", "Section", "Day1", "Time1", "Day2", "Time2", "Room1", "Room2", "Faculty Name", "Credit"]
    st.dataframe(st.session_state.selected_courses[selected_display_cols].reset_index(drop=True))

    # Select courses to remove
    selected_options = st.multiselect(
        "Select course(s) to remove",
        st.session_state.selected_courses.apply(lambda row: f"{row['Course Code']} ({row['Section']})", axis=1).tolist()
    )

    st.markdown("<br><br>", unsafe_allow_html=True)  # Added vertical spacing before the button

    if st.button("❌ Remove Selected Course(s)"):
        if selected_options:
            for opt in selected_options:
                code, section = opt.split(" (")
                section = section.rstrip(")")
                st.session_state.selected_courses = st.session_state.selected_courses[
                    ~(
                        (st.session_state.selected_courses["Course Code"] == code) &
                        (st.session_state.selected_courses["Section"] == section)
                    )
                ].reset_index(drop=True)
            st.success(f"✅ Removed {len(selected_options)} course(s).")
        else:
            st.warning("⚠️ Please select course(s) to remove.")

    csv = st.session_state.selected_courses.to_csv(index=False)
    st.download_button("⬇️ Download Selection as CSV", csv, file_name="my_courses.csv", mime='text/csv')

    if st.button("🗑️ Clear All Selected Courses"):
        st.session_state.selected_courses = pd.DataFrame(columns=courses_df.columns)
        st.success("✅ All selected courses have been cleared.")
