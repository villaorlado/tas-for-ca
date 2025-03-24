import streamlit as st
from PIL import Image

# Load the image
image_path = "../5_results_render/grid_image.jpg"  # Replace with the path to your image
image = Image.open(image_path)

# Create a layout with columns for overlaying checkboxes on top of the image
col1, col2 = st.columns([3, 1])  # Image column and control column for checkboxes

# Show the image in the first column
col1.image(image, caption="Your Image", use_column_width=True)

# In the second column, place checkboxes on top of the image
with col2:
    checkbox1 = st.checkbox("Option 1")
    checkbox2 = st.checkbox("Option 2")
    checkbox3 = st.checkbox("Option 3")

# Show the selected checkbox values
st.write(f"Option 1 selected: {checkbox1}")
st.write(f"Option 2 selected: {checkbox2}")
st.write(f"Option 3 selected: {checkbox3}")
