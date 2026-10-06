import streamlit as st
import sqlite3
import os
from datetime import date
from difflib import SequenceMatcher
from PIL import Image

# =========================================================
# PAGE SETTINGS
# =========================================================

st.set_page_config(
    page_title="FindIt AI",
    page_icon="🔎",
    layout="wide"
)

# =========================================================
# FOLDERS
# =========================================================

IMAGE_FOLDER = "images"

if not os.path.exists(IMAGE_FOLDER):
    os.makedirs(IMAGE_FOLDER)

# =========================================================
# DATABASE
# =========================================================

def create_database():

    connection = sqlite3.connect("findit.db")

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_type TEXT NOT NULL,
            item_name TEXT NOT NULL,
            description TEXT,
            location TEXT,
            item_date TEXT,
            contact TEXT,
            image TEXT
        )
    """)

    connection.commit()
    connection.close()


create_database()

# =========================================================
# ADD ITEM
# =========================================================

def add_item(
    item_type,
    item_name,
    description,
    location,
    item_date,
    contact,
    image_path
):

    connection = sqlite3.connect("findit.db")

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO items
        (
            item_type,
            item_name,
            description,
            location,
            item_date,
            contact,
            image
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        item_type,
        item_name,
        description,
        location,
        item_date,
        contact,
        image_path
    ))

    connection.commit()
    connection.close()

# =========================================================
# GET ITEMS
# =========================================================

def get_items():

    connection = sqlite3.connect("findit.db")

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            item_type,
            item_name,
            description,
            location,
            item_date,
            contact,
            image
        FROM items
        ORDER BY id DESC
    """)

    data = cursor.fetchall()

    connection.close()

    return data

# =========================================================
# AI SIMILARITY
# =========================================================

def similarity(text1, text2):

    text1 = str(text1).lower()
    text2 = str(text2).lower()

    return SequenceMatcher(
        None,
        text1,
        text2
    ).ratio()

# =========================================================
# AI MATCHING
# =========================================================

def find_matches(
    lost_name,
    lost_description,
    lost_location
):

    items = get_items()

    matches = []

    for item in items:

        item_id = item[0]
        item_type = item[1]
        item_name = item[2]
        description = item[3] or ""
        location = item[4] or ""

        # Only compare with found items
        if item_type != "Found":
            continue

        name_score = similarity(
            lost_name,
            item_name
        )

        description_score = similarity(
            lost_description,
            description
        )

        location_score = similarity(
            lost_location,
            location
        )

        final_score = (
            name_score * 0.50
            +
            description_score * 0.30
            +
            location_score * 0.20
        )

        matches.append({
            "score": final_score,
            "id": item_id,
            "name": item_name,
            "description": description,
            "location": location,
            "date": item[5],
            "contact": item[6],
            "image": item[7]
        })

    matches.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return matches[:5]

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

.main-title {
    font-size: 45px;
    font-weight: bold;
}

.subtitle {
    font-size: 20px;
}

.card {
    padding: 20px;
    border-radius: 15px;
    border: 1px solid #ddd;
    margin-bottom: 15px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("🔎 FindIt AI")

st.sidebar.write(
    "Smart Lost & Found System"
)

st.sidebar.divider()

page = st.sidebar.radio(
    "Choose a page",
    [
        "🏠 Home",
        "📢 Report Lost Item",
        "📦 Report Found Item",
        "🔍 Search Items",
        "🤖 AI Match",
        "📊 Dashboard"
    ]
)

# =========================================================
# HOME
# =========================================================

if page == "🏠 Home":

    st.markdown(
        '<div class="main-title">🔎 FindIt AI</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        'Smart Lost & Found Management System'
        '</div>',
        unsafe_allow_html=True
    )

    st.divider()

    items = get_items()

    lost_count = len([
        item for item in items
        if item[1] == "Lost"
    ])

    found_count = len([
        item for item in items
        if item[1] == "Found"
    ])

    total_count = len(items)

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "📢 Lost Items",
            lost_count
        )

    with col2:

        st.metric(
            "📦 Found Items",
            found_count
        )

    with col3:

        st.metric(
            "📋 Total Reports",
            total_count
        )

    st.divider()

    st.subheader(
        "🌟 How FindIt AI Works"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.info(
            "📢 **Report**\n\n"
            "Report your lost or found item."
        )

    with col2:

        st.info(
            "🔍 **Search**\n\n"
            "Search through reported items."
        )

    with col3:

        st.info(
            "🤖 **AI Match**\n\n"
            "Find similar items automatically."
        )

# =========================================================
# REPORT LOST ITEM
# =========================================================

elif page == "📢 Report Lost Item":

    st.title("📢 Report Lost Item")

    st.write(
        "Enter the details of your lost item."
    )

    with st.form("lost_form"):

        item_name = st.text_input(
            "Item Name *",
            placeholder="Example: Black Wallet"
        )

        description = st.text_area(
            "Description",
            placeholder=(
                "Example: Black leather wallet "
                "with college ID"
            )
        )

        location = st.text_input(
            "Lost Location",
            placeholder="Example: College Library"
        )

        item_date = st.date_input(
            "Lost Date",
            date.today()
        )

        contact = st.text_input(
            "Contact Information",
            placeholder="Phone number or email"
        )

        uploaded_image = st.file_uploader(
            "Upload Item Image",
            type=["jpg", "jpeg", "png"]
        )

        submit = st.form_submit_button(
            "📢 Report Lost Item"
        )

        if submit:

            if item_name.strip() == "":

                st.error(
                    "Please enter the item name."
                )

            else:

                image_path = ""

                if uploaded_image:

                    image_path = os.path.join(
                        IMAGE_FOLDER,
                        "lost_"
                        + uploaded_image.name
                    )

                    with open(
                        image_path,
                        "wb"
                    ) as file:

                        file.write(
                            uploaded_image.getbuffer()
                        )

                add_item(
                    "Lost",
                    item_name,
                    description,
                    location,
                    str(item_date),
                    contact,
                    image_path
                )

                st.success(
                    "✅ Lost item reported successfully!"
                )

# =========================================================
# REPORT FOUND ITEM
# =========================================================

elif page == "📦 Report Found Item":

    st.title("📦 Report Found Item")

    st.write(
        "Enter the details of the item you found."
    )

    with st.form("found_form"):

        item_name = st.text_input(
            "Item Name *",
            placeholder="Example: Black Wallet"
        )

        description = st.text_area(
            "Description",
            placeholder=(
                "Example: Black leather wallet "
                "with college ID"
            )
        )

        location = st.text_input(
            "Found Location",
            placeholder="Example: College Library"
        )

        item_date = st.date_input(
            "Found Date",
            date.today()
        )

        contact = st.text_input(
            "Contact Information",
            placeholder="Phone number or email"
        )

        uploaded_image = st.file_uploader(
            "Upload Item Image",
            type=["jpg", "jpeg", "png"]
        )

        submit = st.form_submit_button(
            "📦 Report Found Item"
        )

        if submit:

            if item_name.strip() == "":

                st.error(
                    "Please enter the item name."
                )

            else:

                image_path = ""

                if uploaded_image:

                    image_path = os.path.join(
                        IMAGE_FOLDER,
                        "found_"
                        + uploaded_image.name
                    )

                    with open(
                        image_path,
                        "wb"
                    ) as file:

                        file.write(
                            uploaded_image.getbuffer()
                        )

                add_item(
                    "Found",
                    item_name,
                    description,
                    location,
                    str(item_date),
                    contact,
                    image_path
                )

                st.success(
                    "✅ Found item reported successfully!"
                )

# =========================================================
# SEARCH
# =========================================================

elif page == "🔍 Search Items":

    st.title("🔍 Search Lost & Found Items")

    search = st.text_input(
        "Search by item name, description or location",
        placeholder="Example: wallet"
    )

    items = get_items()

    if search:

        results = []

        for item in items:

            complete_text = " ".join(
                str(value)
                for value in item
            ).lower()

            if search.lower() in complete_text:

                results.append(item)

    else:

        results = items

    if not results:

        st.warning(
            "No items found."
        )

    for item in results:

        col1, col2 = st.columns([1, 3])

        with col1:

            if item[7] and os.path.exists(item[7]):

                st.image(
                    item[7],
                    width=180
                )

            else:

                st.write("🖼️ No image")

        with col2:

            if item[1] == "Lost":

                st.warning(
                    "📢 LOST ITEM"
                )

            else:

                st.success(
                    "📦 FOUND ITEM"
                )

            st.subheader(
                item[2]
            )

            st.write(
                "**Description:**",
                item[3]
            )

            st.write(
                "**Location:**",
                item[4]
            )

            st.write(
                "**Date:**",
                item[5]
            )

            st.write(
                "**Contact:**",
                item[6]
            )

        st.divider()

# =========================================================
# AI MATCH
# =========================================================

elif page == "🤖 AI Match":

    st.title("🤖 AI Smart Matching")

    st.write(
        "Enter your lost item details. "
        "FindIt AI compares them with reported "
        "found items."
    )

    lost_name = st.text_input(
        "Lost Item Name",
        placeholder="Example: Black Wallet"
    )

    lost_description = st.text_area(
        "Description",
        placeholder="Example: Black leather wallet"
    )

    lost_location = st.text_input(
        "Location",
        placeholder="Example: College Library"
    )

    if st.button(
        "🤖 Find Possible Matches"
    ):

        if not lost_name.strip():

            st.error(
                "Please enter the item name."
            )

        else:

            matches = find_matches(
                lost_name,
                lost_description,
                lost_location
            )

            if not matches:

                st.warning(
                    "No found items are available."
                )

            else:

                st.subheader(
                    "🎯 Possible Matches"
                )

                for match in matches:

                    score = match["score"] * 100

                    if score >= 70:

                        st.success(
                            f"🟢 Strong Match — "
                            f"{score:.1f}%"
                        )

                    elif score >= 40:

                        st.warning(
                            f"🟡 Possible Match — "
                            f"{score:.1f}%"
                        )

                    else:

                        st.info(
                            f"🔵 Low Match — "
                            f"{score:.1f}%"
                        )

                    col1, col2 = st.columns(
                        [1, 3]
                    )

                    with col1:

                        if (
                            match["image"]
                            and
                            os.path.exists(
                                match["image"]
                            )
                        ):

                            st.image(
                                match["image"],
                                width=160
                            )

                    with col2:

                        st.subheader(
                            match["name"]
                        )

                        st.write(
                            "**Description:**",
                            match["description"]
                        )

                        st.write(
                            "**Location:**",
                            match["location"]
                        )

                        st.write(
                            "**Date:**",
                            match["date"]
                        )

                        st.progress(
                            min(
                                int(score),
                                100
                            )
                        )

                    st.divider()

# =========================================================
# DASHBOARD
# =========================================================

elif page == "📊 Dashboard":

    st.title("📊 FindIt AI Dashboard")

    items = get_items()

    lost = [
        item for item in items
        if item[1] == "Lost"
    ]

    found = [
        item for item in items
        if item[1] == "Found"
    ]

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "📋 Total Reports",
            len(items)
        )

    with col2:

        st.metric(
            "📢 Lost",
            len(lost)
        )

    with col3:

        st.metric(
            "📦 Found",
            len(found)
        )

    st.divider()

    st.subheader(
        "📋 Recent Reports"
    )

    if not items:

        st.info(
            "No reports available yet."
        )

    else:

        for item in items[:10]:

            if item[1] == "Lost":

                st.write(
                    f"📢 **Lost:** {item[2]} "
                    f"| 📍 {item[4]} "
                    f"| 📅 {item[5]}"
                )

            else:

                st.write(
                    f"📦 **Found:** {item[2]} "
                    f"| 📍 {item[4]} "
                    f"| 📅 {item[5]}"
                )

