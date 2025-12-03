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
    st.error("Файл alzheimers_disease_data.csv не найден! Проверьте название и расположение файла.")
    st.stop()

st.subheader("Настройки таблицы")

# --------------------
# Фильтры таблицы
# --------------------
if st.checkbox("Удалить дубликаты"):
    data = data.drop_duplicates()

if st.checkbox("Удалить строки с пропущенными значениями"):
    data = data.dropna()

# --------------------
# Выбор столбцов
# --------------------
if 'selected_columns' not in st.session_state:
    st.session_state.selected_columns = data.columns[:5].tolist()

# Кнопка "All"
if st.button("All"):
    st.session_state.selected_columns = data.columns.tolist()

# Multiselect с привязкой к session_state
st.session_state.selected_columns = st.multiselect(
    "Выберите столбцы для отображения",
    options=data.columns,
    default=st.session_state.selected_columns
)

filtered_data = data[st.session_state.selected_columns]

# --------------------
# Ограничение по количеству строк
# --------------------
num_rows = st.slider(
    "Количество первых строк для отображения",
    min_value=5,
    max_value=len(filtered_data),
    value=20
)
display_data = filtered_data.head(num_rows)

# --------------------
# Группировка по столбцам
# --------------------
if st.checkbox("Группировка по столбцам"):
    # Все текстовые столбцы
    categorical_cols = data.select_dtypes('object').columns.tolist()
    
    # Числовые столбцы с небольшим числом уникальных значений как категориальные
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
# Отображение таблицы
# --------------------
st.subheader("Таблица данных")
st.dataframe(display_data)

# --------------------
# Кнопка для скачивания CSV
# --------------------
csv = display_data.to_csv(index=False)
st.download_button("Скачать CSV", csv, "filtered_data.csv", "text/csv")
