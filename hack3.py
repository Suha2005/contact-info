import streamlit as st
import sqlite3
import base64
from PIL import Image
import io

# Database setup
def init_db():
    conn = sqlite3.connect('contacts.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            first_meet_place TEXT,
            how_close TEXT,
            reason_close TEXT,
            profile_picture TEXT,
            notes TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Image handling
def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def base64_to_image(base64_str):
    try:
        missing_padding = len(base64_str) % 4
        if missing_padding:
            base64_str += "=" * (4 - missing_padding)
        
        # Decode the base64 string
        img_data = base64.b64decode(base64_str)
        
        # Try opening the image to see if it's valid
        img = Image.open(io.BytesIO(img_data))
        img.verify()  # Verify if it's a valid image
        return img_data
    except Exception as e:
        st.error(f"Error loading image: {e}")
        return None

# Set sidebar background
def set_sidebar_bg(image_file):
    with open(image_file, "rb") as image:
        base64_image = base64.b64encode(image.read()).decode()
    
    sidebar_style = f"""
        <style>
        [data-testid="stSidebar"] {{
            background-image: url("data:image/jpg;base64,{base64_image}");
            background-size: cover;
            padding: 10px !important;
        }}
        </style>
    """
    st.markdown(sidebar_style, unsafe_allow_html=True)

# Streamlit UI
st.set_page_config(page_title="Contact Manager", page_icon="📇")
set_sidebar_bg("sidebar_bg.jpg")  # Set sidebar background image

def main():
    st.title("Contact Relationship Manager 📇")
    
    menu = ["Add Contact", "View Contacts", "Delete Contact", "About"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Add Contact":
        st.header("Add New Contact")
        with st.form("contact_form"):
            name = st.text_input("Name")
            col1, col2 = st.columns(2)
            phone = col1.text_input("Phone")
            email = col2.text_input("Email")
            first_meet = st.text_input("First Meeting Place")
            how_close = st.text_input("How did you get close?")
            reason_close = st.text_input("Reason for getting close")
            notes = st.text_area("Notes")
            profile_pic = st.file_uploader("Profile Picture", type=["jpg", "png", "jpeg"])
            
            if st.form_submit_button("Save Contact"):
                conn = sqlite3.connect('contacts.db')
                c = conn.cursor()
                
                # Handle image
                img_str = None
                if profile_pic is not None:
                    image = Image.open(profile_pic)
                    img_str = image_to_base64(image)
                
                # Insert into database
                c.execute('''
                    INSERT INTO contacts 
                    (name, phone, email, first_meet_place, how_close, reason_close, profile_picture, notes)
                    VALUES (?,?,?,?,?,?,?,?)
                ''', (name, phone, email, first_meet, how_close, reason_close, img_str, notes))
                
                conn.commit()
                conn.close()
                st.success("Contact saved successfully!")

    elif choice == "View Contacts":
        st.header("Your Contacts")
        conn = sqlite3.connect('contacts.db')
        c = conn.cursor()
        c.execute("SELECT * FROM contacts")
        contacts = c.fetchall()
        
        if not contacts:
            st.warning("No contacts found")
        else:
            for contact in contacts:
                with st.expander(f"{contact[1]} - {contact[2]}"):
                    col1, col2 = st.columns([1, 3])
                    
                    with col1:
                        if contact[7]:
                            img_data = base64_to_image(contact[7])
                            if img_data:
                                st.image(img_data, caption="Profile Picture", use_container_width=True)
                    
                    with col2:
                        st.markdown(f"""
                        **Email:** {contact[3]}  
                        **First Met At:** {contact[4]}  
                        **How You Got Close:** {contact[5]}  
                        **Reason for Closeness:** {contact[6]}  
                        **Notes:**  
                        {contact[8]}
                        """)
                    
                    st.write("---")
    
    elif choice == "Delete Contact":
        st.header("Delete Contact")
        conn = sqlite3.connect('contacts.db')
        c = conn.cursor()
        c.execute("SELECT id, name FROM contacts")
        contacts = c.fetchall()
        
        contact_dict = {f"{contact[1]} (ID: {contact[0]})": contact[0] for contact in contacts}
        selected_contact = st.selectbox("Select a contact to delete", list(contact_dict.keys()))
        
        if st.button("Delete Contact"):
            c.execute("DELETE FROM contacts WHERE id=?", (contact_dict[selected_contact],))
            conn.commit()
            conn.close()
            st.success("Contact deleted successfully!")
            st.experimental_rerun()
    
    elif choice == "About":
        st.header("About")
        st.markdown("""
        **Contact Relationship Manager**  
        Built with Streamlit  
        Features:
        - Store contact details
        - Track relationship history
        - Add profile pictures
        - Delete unwanted contacts
        - Persistent SQLite storage
        """)

if __name__ == "__main__":
    main()
