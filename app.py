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

all_columns = data.columns.tolist()

# ------------------------
# Выбор столбцов
# ------------------------
st.subheader("Выбор столбцов")

col1, col2 = st.columns([3, 1])

with col1:
    selected_columns = st.multiselect(
        "Выберите столбцы",
        all_columns,
        default=all_columns[:5]
    )

with col2:
    if st.button("Все столбцы"):
        selected_columns = all_columns

if not selected_columns:
    st.warning("Выберите хотя бы один столбец.")
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
# Простая группировка
# ------------------------
st.subheader("Группировка данных (простая)")

group_enabled = st.checkbox("Включить группировку")

if group_enabled:
    # Категориальные + те числовые, у которых <=20 уникальных значений
    categorical = data.select_dtypes("object").columns.tolist()
    for col in data.select_dtypes("number").columns:
        if data[col].nunique() <= 20:
            categorical.append(col)

    if len(categorical) == 0:
        st.info("Нет подходящих столбцов для группировки.")
    else:
        group_cols = st.multiselect(
            "Столбцы для группировки (1–2 столбца)",
            categorical,
            max_selections=2
        )

        numeric_cols = data.select_dtypes("number").columns.tolist()

        if group_cols:
            agg_col = st.selectbox(
                "Столбец для вычисления среднего",
                numeric_cols
            )

            grouped = data.groupby(group_cols)[agg_col].mean().reset_index()

            st.write("Результат группировки:")
            st.dataframe(grouped)

            # Используем сгруппированные данные в графиках
            filtered = grouped

# ------------------------
# Таблица данных
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
    ["Bar chart", "Histogram", "Box plot", "Scatter plot", "Line chart", "Pie chart"]
)

numeric_cols = data.select_dtypes("number").columns.tolist()
all_cols = data.columns.tolist()

# BAR
if chart_type == "Bar chart":
    x = st.selectbox("X:", all_cols)
    y = st.selectbox("Y:", numeric_cols)
    fig = px.bar(display_data, x=x, y=y)
    st.plotly_chart(fig)

# HISTOGRAM
elif chart_type == "Histogram":
    col = st.selectbox("Столбец:", numeric_cols)
    fig = px.histogram(display_data, x=col)
    st.plotly_chart(fig)

# BOX
elif chart_type == "Box plot":
    x = st.selectbox("Группировка:", all_cols)
    y = st.selectbox("Значения:", numeric_cols)
    fig = px.box(display_data, x=x, y=y)
    st.plotly_chart(fig)

# SCATTER
elif chart_type == "Scatter plot":
    x = st.selectbox("X:", numeric_cols)
    y = st.selectbox("Y:", numeric_cols)
    color = st.selectbox("Цвет:", [None] + all_cols)
    fig = px.scatter(display_data, x=x, y=y, color=color)
    st.plotly_chart(fig)

# LINE
elif chart_type == "Line chart":
    x = st.selectbox("X:", all_cols)
    y = st.selectbox("Y:", numeric_cols)
    fig = px.line(display_data, x=x, y=y)
    st.plotly_chart(fig)

# PIE
elif chart_type == "Pie chart":
    labels = st.selectbox("Категории:", all_cols)
    values = st.selectbox("Значения:", numeric_cols)
    fig = px.pie(display_data, names=labels, values=values)
    st.plotly_chart(fig)

# ------------------------
# Скачать файл
# ------------------------
csv = display_data.to_csv(index=False)
st.download_button("Скачать CSV", csv, "data.csv", "text/csv")
