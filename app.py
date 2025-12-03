import pandas as pd
import streamlit as st

# Загружаем данные
data = pd.read_csv('alzheimer.csv')

st.title("Alzheimer Dataset Viewer")

# Показываем таблицу
st.dataframe(data)

# Пример простого графика
st.bar_chart(data.select_dtypes('number'))
