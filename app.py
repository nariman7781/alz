import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Alzheimer Dataset Viewer", layout="wide")

st.title("Alzheimer Dataset Interactive Viewer")

# Загружаем данные

try:
data = pd.read_csv('alzheimers_disease_data.csv')
except FileNotFoundError:
st.error("Файл alzheimers_disease_data.csv не найден! Проверьте название и расположение файла.")
st.stop()

# Показываем фильтр для выбора столбцов

numeric_cols = data.select_dtypes('number').columns.tolist()
selected_cols = st.multiselect("Выберите числовые столбцы для графика", numeric_cols, default=numeric_cols[:3])

# Ограничиваем количество строк для графика для ускорения работы

max_rows = st.slider("Количество строк для графика", min_value=10, max_value=min(1000, len(data)), value=200)

# Таблица

st.subheader("Данные")
st.dataframe(data.head(max_rows))

# График

if selected_cols:
st.subheader("График выбранных столбцов")
fig = px.bar(data.head(max_rows), x=data.index[:max_rows], y=selected_cols)
st.plotly_chart(fig, use_container_width=True)
else:
st.info("Выберите хотя бы один столбец для построения графика.")

