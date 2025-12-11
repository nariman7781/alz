import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Alzheimer Dataset Viewer", layout="wide")
st.title("Alzheimer Dataset Viewer")

# ------------------------
# Загрузка файла
# ------------------------
try:
    data = pd.read_csv("alzheimers_disease_data.csv")
except FileNotFoundError:
    st.error("Файл alzheimers_disease_data.csv не найден.")
    st.stop()

# ------------------------
# Выбор столбцов
# ------------------------
st.subheader("Выбор столбцов")

all_cols = data.columns.tolist()

selected_columns = st.multiselect(
    "Выберите столбцы",
    all_cols,
    default=all_cols[:5]
)

if len(selected_columns) == 0:
    st.warning("Выберите хотя бы один столбец")
    st.stop()

filtered = data[selected_columns]

# ------------------------
# Фильтры
# ------------------------
st.subheader("Фильтры")

col1, col2 = st.columns(2)

with col1:
    if st.checkbox("Удалить дубликаты"):
        filtered = filtered.drop_duplicates()

with col2:
    if st.checkbox("Удалить строки с пропусками"):
        filtered = filtered.dropna()

# ------------------------
# Отображение таблицы
# ------------------------
st.subheader("Таблица данных")

rows = st.slider(
    "Количество строк",
    5,
    len(filtered),
    20
)

display_data = filtered.head(rows)
st.dataframe(display_data)

# ------------------------
# Графики
# ------------------------
st.subheader("Графики")

chart_type = st.selectbox(
    "Тип графика",
    ["Bar chart", "Histogram", "Box plot", "Scatter plot", "Line chart"]
)

numeric = data.select_dtypes("number").columns.tolist()
all_cols = data.columns.tolist()

if chart_type == "Bar chart":
    x = st.selectbox("X:", all_cols)
    y = st.selectbox("Y:", numeric)
    fig = px.bar(display_data, x=x, y=y)
    st.plotly_chart(fig)

elif chart_type == "Histogram":
    col = st.selectbox("Столбец:", numeric)
    fig = px.histogram(display_data, x=col)
    st.plotly_chart(fig)

elif chart_type == "Box plot":
    x = st.selectbox("Группировка:", all_cols)
    y = st.selectbox("Значения:", numeric)
    fig = px.box(display_data, x=x, y=y)
    st.plotly_chart(fig)

elif chart_type == "Scatter plot":
    x = st.selectbox("X:", numeric)
    y = st.selectbox("Y:", numeric)
    color = st.selectbox("Цвет:", [None] + all_cols)
    fig = px.scatter(display_data, x=x, y=y, color=color)
    st.plotly_chart(fig)

elif chart_type == "Line chart":
    x = st.selectbox("X:", all_cols)
    y = st.selectbox("Y:", numeric)
    fig = px.line(display_data, x=x, y=y)
    st.plotly_chart(fig)

# ------------------------
# Скачать CSV
# ------------------------
csv = display_data.to_csv(index=False)
st.download_button("Скачать CSV", csv, "data.csv", "text/csv")
