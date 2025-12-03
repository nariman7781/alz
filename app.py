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

csv = display_data.to_csv(index=False)
st.download_button("Скачать CSV", csv, "filtered_data.csv", "text/csv")
