import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Alzheimer Dataset Viewer", layout="wide")
st.title("Alzheimer Dataset Viewer")

# ------------------------
# Загружаем данные
# ------------------------
try:
    original_data = pd.read_csv("alzheimers_disease_data.csv")
except FileNotFoundError:
    st.error("Файл alzheimers_disease_data.csv не найден!")
    st.stop()

# копия чтобы всегда хранить оригинал
data = original_data.copy()

# ------------------------
# Глобальная очистка данных (на всю таблицу)
# ------------------------
st.subheader("Очистка данных (вся таблица)")

col1, col2 = st.columns(2)

with col1:
    remove_global_dupes = st.checkbox("Удалить дубликаты (вся таблица)")

with col2:
    remove_global_nans = st.checkbox("Удалить строки с пропусками (вся таблица)")

if remove_global_dupes:
    before = len(data)
    data = data.drop_duplicates()
    st.success(f"Удалено дубликатов: {before - len(data)}")

if remove_global_nans:
    before = len(data)
    data = data.dropna()
    st.success(f"Удалено строк с пропусками: {before - len(data)}")

# ------------------------
# Выбор столбцов и фильтры (только для отображения)
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

# Таблица для отображения
num_rows = st.slider("Количество первых строк для отображения", 5, len(filtered_data), 20)
display_data = filtered_data.head(num_rows)

st.subheader("Таблица данных")
st.dataframe(display_data)

# ------------------------
# Группировка (работает только с основной таблицей data)
# ------------------------
st.subheader("Группировка данных")

grouped_table = None
if st.checkbox("Включить группировку (на чистой таблице)"):

    # Категориальные колонки
    cat_cols = data.select_dtypes("object").columns.tolist()
    for col in data.select_dtypes("number").columns:
        if data[col].nunique() <= 20:
            cat_cols.append(col)

    if cat_cols:
        group_cols = st.multiselect(
            "Столбцы для группировки",
            cat_cols,
            default=cat_cols[:1]
        )

        num_cols = data.select_dtypes("number").columns.tolist()

        if group_cols and num_cols:
            agg_col = st.selectbox("Числовой столбец для агрегации", num_cols)

            # ЧИСТАЯ ГРУППИРОВКА — без удаления пропусков/дубликатов
            grouped_table = data.groupby(group_cols)[agg_col].mean().reset_index()

            st.write("Результат группировки:")
            st.dataframe(grouped_table)

        else:
            st.warning("Выберите столбцы корректно.")
    else:
        st.info("Нет подходящих столбцов для группировки")

# ------------------------
# Графики (рисуются с основной таблицы data)
# ------------------------
st.subheader("Графики")
chart_type = st.selectbox(
    "Выберите тип графика",
    ["Bar chart", "Histogram", "Box plot", "Scatter plot", "Line chart", "Pie chart"]
)

numeric_cols = data.select_dtypes("number").columns.tolist()
all_cols = data.columns.tolist()

if chart_type == "Bar chart":
    x_col = st.selectbox("X (категориальный)", all_cols)
    y_col = st.selectbox("Y (числовой)", numeric_cols)
    fig = px.bar(data, x=x_col, y=y_col)
    st.plotly_chart(fig, use_container_width=True)

elif chart_type == "Histogram":
    col = st.selectbox("Столбец", numeric_cols)
    bins = st.slider("Количество корзин", 5, 100, 30)
    fig = px.histogram(data, x=col, nbins=bins)
    st.plotly_chart(fig, use_container_width=True)

elif chart_type == "Box plot":
    x_col = st.selectbox("Группировка", all_cols)
    y_col = st.selectbox("Значения", numeric_cols)
    fig = px.box(data, x=x_col, y=y_col)
    st.plotly_chart(fig, use_container_width=True)

elif chart_type == "Scatter plot":
    x = st.selectbox("X", numeric_cols)
    y = st.selectbox("Y", numeric_cols)
    color = st.selectbox("Цвет (опционально)", [None] + all_cols)
    fig = px.scatter(data, x=x, y=y, color=color) if color else px.scatter(data, x=x, y=y)
    st.plotly_chart(fig, use_container_width=True)

elif chart_type == "Line chart":
    x = st.selectbox("X", all_cols)
    y = st.selectbox("Y", numeric_cols)
    fig = px.line(data, x=x, y=y)
    st.plotly_chart(fig, use_container_width=True)

elif chart_type == "Pie chart":
    labels = st.selectbox("Категории", all_cols)
    values = st.selectbox("Значения", numeric_cols)
    fig = px.pie(data, names=labels, values=values)
    st.plotly_chart(fig, use_container_width=True)

# ------------------------
# Скачивание CSV (только отображаемых данных)
# ------------------------
csv = display_data.to_csv(index=False)
st.download_button("Скачать CSV", csv, "filtered_data.csv", "text/csv")
