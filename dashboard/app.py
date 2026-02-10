import streamlit as st
from db.mongo import vehicles_col

st.title("Audi Used Cars")

cars = list(vehicles_col.find({"status": "active"}))
st.dataframe(cars)