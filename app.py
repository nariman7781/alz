import pandas as pd
import streamlit as st

st.set_page_config(page_title="Alzheimer Dataset Viewer", layout="wide")
st.title("Alzheimer Dataset Interactive Viewer")

# Загружаем данные
try:
    data = pd.read_csv('alzheimers_disease_data.csv')
except FileNotFoundError:
    st.error("Файл alzheimers_disease_data.csv не найден! Проверьте название и расположение файла.")
    st.stop()

st.subheader("Настройки таблицы")

# Фильтры и работа с таблицей
if st.checkbox("Удалить дубликаты"):
    data = data.drop_duplicates()

if st.checkbox("Удалить строки с пропущенными значениями"):
    data = data.dropna()

# Инициализация состояния для выбранных столбцов
if 'selected_columns' not in st.session_state:
    st.session_state.selected_columns = data.columns[:5].tolist()

# Кнопка "All"
if st.button("All"):
    st.session_state.selected_columns = data.columns.tolist()

# Multiselect для выбора столбцов, с привязкой к session_state
st.session_state.selected_columns = st.multiselect(
    "Выберите столбцы для отображения",
    options=data.columns,
    default=st.session_state.selected_columns
)

filtered_data = data[st.session_state.selected_columns]

# Ограничение по количеству строк
num_rows = st.slider("Количество первых строк для отображения", min_value=5, max_value=len(filtered_data), value=20)
display_data = filtered_data.head(num_rows)

# Простейшее объединение / группировка
if st.checkbox("Группировка по категориальному столбцу"):
    cat_column = st.selectbox("Выберите столбец для группировки", options=data.select_dtypes('object').columns.tolist())
    agg_column = st.selectbox("Выберите числовой столбец для агрегации", options=data.select_dtypes('number').columns.tolist())
    display_data = data.groupby(cat_column)[agg_column].mean().reset_index()
    st.write(f"Группировка по {cat_column}, среднее значение {agg_column}")

# Отображаем таблицу
st.subheader("Таблица данных")
st.dataframe(display_data)

# Кнопка для скачивания
csv = display_data.to_csv(index=False)
st.download_button("Скачать CSV", csv, "filtered_data.csv", "text/csv")
