import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Alzheimer Dataset Viewer", layout="wide")
st.title("Alzheimer Dataset Viewer")

# ------------------------
# Загружаем данные
# ------------------------
try:
    data = pd.read_csv("alzheimers_disease_data.csv")
except FileNotFoundError:
    st.error("Файл alzheimers_disease_data.csv не найден!")
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
    remove_dupes = st.checkbox("Удалить дубликаты")
with col2:
    remove_na = st.checkbox("Удалить строки с пропусками")

# Применяем фильтры к таблице
if remove_dupes:
    filtered_data = filtered_data.drop_duplicates()
if remove_na:
    filtered_data = filtered_data.dropna()

# ------------------------
# Отображение основной таблицы
# ------------------------
st.subheader("Таблица данных")
num_rows = st.slider("Количество первых строк для отображения", 5, len(filtered_data), 20)
display_data = filtered_data.head(num_rows)
st.dataframe(display_data)

# ------------------------
# Группировка из базы данных (отдельная таблица)
# ------------------------
st.subheader("Группировка данных")
grouped_table = None
if st.checkbox("Включить группировку (не зависит от фильтров)"):
    # Все столбцы базы
    all_cols = data.columns.tolist()

    # Категориальные для группировки
    cat_cols = data.select_dtypes("object").columns.tolist()
    for col in data.select_dtypes("number").columns:
        if data[col].nunique() <= 20:
            cat_cols.append(col)

    if cat_cols:
        group_cols = st.multiselect(
            "Выберите столбцы для группировки",
            cat_cols,
            default=cat_cols[:1]
        )
        num_cols = data.select_dtypes("number").columns.tolist()
        if group_cols and num_cols:
            agg_col = st.selectbox("Числовой столбец для агрегации", num_cols)
            # Исключаем agg_col из группировки, если совпадает
            group_cols_for_grouping = [col for col in group_cols if col != agg_col]

            grouped_table = data.groupby(group_cols_for_grouping)[agg_col].mean().reset_index()
            st.write("Результат группировки:")
            st.dataframe(grouped_table)
        else:
            st.warning("Выберите хотя бы один столбец для группировки и один числовой для агрегации")
    else:
        st.info("Нет подходящих столбцов для группировки")

# ------------------------
# Графики (берутся из базы данных)
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
    if color:
        fig = px.scatter(data, x=x, y=y, color=color)
    else:
        fig = px.scatter(data, x=x, y=y)
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
# Скачивание CSV (только основной таблицы)
# ------------------------
csv = display_data.to_csv(index=False)
st.download_button("Скачать CSV", csv, "filtered_data.csv", "text/csv")
