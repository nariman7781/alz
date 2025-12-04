import pandas as pd
import streamlit as st

st.set_page_config(page_title="Alzheimer Dataset Viewer", layout="wide")
st.title("Alzheimer Dataset Interactive Viewer")

# --------------------
# Загружаем данные
# --------------------
try:
    data = pd.read_csv('alzheimers_disease_data.csv')
except FileNotFoundError:
    st.error("Файл alzheimers_disease_data.csv не найден!")
    st.stop()

# --------------------
# Раздел: Фильтры и выбор столбцов
# --------------------
with st.expander("Фильтры и выбор столбцов", expanded=True):
    # Выбор столбцов
    if 'selected_columns' not in st.session_state:
        st.session_state.selected_columns = data.columns[:5].tolist()

    col1, col2 = st.columns([3,1])
    with col1:
        st.session_state.selected_columns = st.multiselect(
            "Выберите столбцы для отображения",
            options=data.columns,
            default=st.session_state.selected_columns
        )
    with col2:
        if st.button("All"):
            st.session_state.selected_columns = data.columns.tolist()

    filtered_data = data[st.session_state.selected_columns]

    # Удаление дубликатов и пропусков
    col1, col2 = st.columns(2)
    with col1:
        remove_dupes = st.checkbox("Удалить дубликаты (по выбранным столбцам)")
        if remove_dupes:
            filtered_data = filtered_data.drop_duplicates()
    with col2:
        remove_na = st.checkbox("Удалить строки с пропущенными значениями (по выбранным столбцам)")
        if remove_na:
            filtered_data = filtered_data.dropna()

# --------------------
# Раздел: Настройки отображения
# --------------------
with st.expander("Настройки отображения таблицы", expanded=True):
    num_rows = st.slider(
        "Количество первых строк для отображения",
        min_value=5,
        max_value=len(filtered_data),
        value=20
    )
    display_data = filtered_data.head(num_rows)

# --------------------
# Раздел: Группировка
# --------------------
with st.expander("Группировка по столбцам", expanded=False):
    if st.checkbox("Включить группировку"):
        # Категориальные столбцы
        categorical_cols = data.select_dtypes('object').columns.tolist()
        for col in data.select_dtypes('number').columns:
            if data[col].nunique() <= 20:
                categorical_cols.append(col)

        if categorical_cols:
            cat_columns = st.multiselect(
                "Выберите столбцы для группировки (можно несколько)",
                options=categorical_cols,
                default=categorical_cols[:1]
            )

            if cat_columns:
                agg_column = st.selectbox(
                    "Выберите числовой столбец для агрегации",
                    options=data.select_dtypes('number').columns.tolist()
                )
                display_data = data.groupby(cat_columns)[agg_column].mean().reset_index()
                st.write(f"Группировка по {', '.join(cat_columns)}, среднее значение {agg_column}")
        else:
            st.info("Нет подходящих столбцов для группировки")

# --------------------
# Раздел: Таблица и скачивание
# --------------------
st.subheader("Таблица данных")
st.dataframe(display_data)

# --------------------
# Раздел: Графики
# --------------------
st.subheader("Графики")

chart_type = st.selectbox(
    "Выберите тип графика",
    [
        "Bar chart / Column chart",
        "Histogram",
        "Box plot",
        "Scatter plot",
        "Line chart"
    ]
)

numeric_cols = data.select_dtypes('number').columns.tolist()
all_cols = data.columns.tolist()

# BAR / COLUMN
if chart_type == "Bar chart / Column chart":
    x_col = st.selectbox("X (категориальный столбец)", all_cols)
    y_col = st.selectbox("Y (числовой столбец)", numeric_cols)

    fig = px.bar(display_data, x=x_col, y=y_col)
    st.plotly_chart(fig, use_container_width=True)

# HISTOGRAM
elif chart_type == "Histogram":
    col = st.selectbox("Столбец для гистограммы", numeric_cols)
    bins = st.slider("Количество корзин (bins)", 5, 100, 30)

    fig = px.histogram(display_data, x=col, nbins=bins)
    st.plotly_chart(fig, use_container_width=True)

# BOX PLOT
elif chart_type == "Box plot":
    y_col = st.selectbox("Числовой столбец", numeric_cols)
    x_col = st.selectbox("Группировка по", all_cols)

    fig = px.box(display_data, x=x_col, y=y_col)
    st.plotly_chart(fig, use_container_width=True)

# SCATTER PLOT
elif chart_type == "Scatter plot":
    x = st.selectbox("X", numeric_cols)
    y = st.selectbox("Y", numeric_cols)

    color = st.selectbox("Цветовая метка (опционально)", [None] + all_cols)

    fig = px.scatter(display_data, x=x, y=y, color=color)
    st.plotly_chart(fig, use_container_width=True)

# LINE CHART
elif chart_type == "Line chart":
    x = st.selectbox("X (обычно время или индекс)", all_cols)
    y = st.selectbox("Y (числовой столбец)", numeric_cols)

    fig = px.line(display_data, x=x, y=y)
    st.plotly_chart(fig, use_container_width=True)


csv = display_data.to_csv(index=False)
st.download_button("Скачать CSV", csv, "filtered_data.csv", "text/csv")
