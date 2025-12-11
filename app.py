import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Alzheimer Dataset Viewer", layout="wide")
st.title("Alzheimer Dataset Viewer")

# ------------------------
# Загрузка данных
# ------------------------
try:
    data = pd.read_csv("alzheimers_disease_data.csv")
except FileNotFoundError:
    st.error("Файл alzheimers_disease_data.csv не найден.")
    st.stop()

# ------------------------
# Выбор столбцов и фильтры
# ------------------------
st.subheader("Выбор столбцов и фильтры")

selected_columns = st.multiselect(
    "Выберите столбцы для отображения",
    data.columns.tolist(),
    default=data.columns[:5]
)

if not selected_columns:
    st.warning("Выберите хотя бы один столбец.")
    st.stop()

filtered_data = data[selected_columns]

col1, col2 = st.columns(2)
with col1:
    if st.checkbox("Удалить дубликаты"):
        filtered_data = filtered_data.drop_duplicates()
with col2:
    if st.checkbox("Удалить строки с пропусками"):
        filtered_data = filtered_data.dropna()

# ------------------------
# Настройка отображения таблицы
# ------------------------
st.subheader("Таблица данных")

num_rows = st.slider(
    "Количество первых строк для отображения",
    min_value=5,
    max_value=len(filtered_data),
    value=20
)

display_data = filtered_data.head(num_rows)
st.dataframe(display_data)

# ------------------------
# Простая группировка
# ------------------------
st.subheader("Группировка данных")

if st.checkbox("Включить группировку"):
    categorical_cols = data.select_dtypes("object").columns.tolist()
    for col in data.select_dtypes("number").columns:
        if data[col].nunique() <= 20:
            categorical_cols.append(col)

    if categorical_cols:
        group_cols = st.multiselect(
            "Выберите столбцы для группировки",
            categorical_cols,
            default=categorical_cols[:1]
        )
        numeric_cols = data.select_dtypes("number").columns.tolist()
        if group_cols:
            agg_col = st.selectbox("Числовой столбец для агрегации", numeric_cols)
            display_data = data.groupby(group_cols)[agg_col].mean().reset_index()
            st.write(f"Группировка по {', '.join(group_cols)}, среднее значение {agg_col}")
    else:
        st.info("Нет подходящих столбцов для группировки")

# ------------------------
# Графики
# ------------------------
st.subheader("Графики")

chart_type = st.selectbox(
    "Выберите тип графика",
    ["Bar chart", "Histogram", "Box plot", "Scatter plot", "Line chart"]
)

numeric_cols = data.select_dtypes("number").columns.tolist()
all_cols = data.columns.tolist()

if chart_type == "Bar chart":
    x_col = st.selectbox("X (категориальный)", all_cols)
    y_col = st.selectbox("Y (числовой)", numeric_cols)
    fig = px.bar(display_data, x=x_col, y=y_col)
    st.plotly_chart(fig, use_container_width=True)

elif chart_type == "Histogram":
    col = st.selectbox("Столбец", numeric_cols)
    bins = st.slider("Количество корзин", 5, 100, 30)
    fig = px.histogram(display_data, x=col, nbins=bins)
    st.plotly_chart(fig, use_container_width=True)

elif chart_type == "Box plot":
    x_col = st.selectbox("Группировка", all_cols)
    y_col = st.selectbox("Значения", numeric_cols)
    fig = px.box(display_data, x=x_col, y=y_col)
    st.plotly_chart(fig, use_container_width=True)

elif chart_type == "Scatter plot":
    x = st.selectbox("X", numeric_cols)
    y = st.selectbox("Y", numeric_cols)
    color = st.selectbox("Цвет (опционально)", [None] + all_cols)
    fig = px.scatter(display_data, x=x, y=y, color=color)
    st.plotly_chart(fig, use_container_width=True)

elif chart_type == "Line chart":
    x = st.selectbox("X", all_cols)
    y = st.selectbox("Y", numeric_cols)
    fig = px.line(display_data, x=x, y=y)
    st.plotly_chart(fig, use_container_width=True)

# ------------------------
# Скачивание CSV
# ------------------------
csv = display_data.to_csv(index=False)
st.download_button("Скачать CSV", csv, "filtered_data.csv", "text/csv")
