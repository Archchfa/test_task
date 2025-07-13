import streamlit as st
import pandas as pd
import plotly.express as px

# Прямые ссылки на raw-файлы на GitHub
fact_table_url = 'https://raw.githubusercontent.com/Archchfa/test_task/main/fact_table_v2.xlsx'
products_url = 'https://raw.githubusercontent.com/Archchfa/test_task/main/products_v2.xlsx'
staff_url = 'https://raw.githubusercontent.com/Archchfa/test_task/main/staff_v2.xlsx'
calendar_url = 'https://raw.githubusercontent.com/Archchfa/test_task/main/calendar_v2.xlsx'
cont_url = 'https://raw.githubusercontent.com/Archchfa/test_task/main/cont_v2.xlsx'

# Загрузка данных из GitHub
fact_with_calendar = pd.read_excel(fact_table_url)
products = pd.read_excel(products_url)
staff = pd.read_excel(staff_url)
calendar = pd.read_excel(calendar_url)
cont = pd.read_excel(cont_url)

# Объединяем fact_with_calendar с products для добавления категории
fact_with_category = pd.merge(fact_with_calendar, products[['productid', 'categoryname']], on='productid', how='left')

# Объединяем fact_with_category с таблицей cont для добавления информации о магазинах
fact_with_full_info = pd.merge(fact_with_category, cont[['name', 'country']], on='name', how='left')

# Фильтруем данные по категории "Женская обувь" и стране "Соединённые Штаты Америки"
filtered_data = fact_with_full_info[
    (fact_with_full_info['categoryname'] == 'Женская обувь') & 
    (fact_with_full_info['country'] == 'Соединённые Штаты Америки')
]

# Агрегируем прибыль по заказчикам
profit_by_customer = filtered_data.groupby('name')['netsalesamount'].sum().reset_index()

# Сортируем по прибыли (чистая прибыль)
profit_by_customer = profit_by_customer.sort_values(by='netsalesamount', ascending=False)

# Топ-10 заказчиков
top_10_customers = profit_by_customer.head(10)

# Заголовок страницы
st.title("Топ-10 прибыльных заказчиков (Женская обувь, США)")

# График: Топ-10 прибыльных заказчиков
st.subheader("Топ-10 прибыльных заказчиков")
fig1 = px.bar(top_10_customers, 
              x='name', 
              y='netsalesamount', 
              orientation='v',  # Вертикальная ориентация (по оси X магазины)
              title="Топ-10 прибыльных заказчиков",
              labels={'netsalesamount': 'Чистая прибыль', 'name': 'Заказчик'},
              color='netsalesamount',
              color_continuous_scale='Blues')

# Поворот оси X, чтобы названия магазинов не накладывались
fig1.update_xaxes(tickangle=45)

# Отображение графика
st.plotly_chart(fig1)
