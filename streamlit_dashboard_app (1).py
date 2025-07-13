
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

# Объединяем fact_with_category с таблицей cont для добавления информации о стране
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
st.title("Анализ прибыльных заказчиков (Женская обувь, США)")

# График 1: Топ-10 прибыльных заказчиков
st.subheader("Топ-10 прибыльных заказчиков")
fig1 = px.bar(top_10_customers, 
              x='netsalesamount', 
              y='name', 
              orientation='h', 
              title="Топ-10 прибыльных заказчиков",
              labels={'netsalesamount': 'Чистая прибыль', 'name': 'Заказчик'},
              color='netsalesamount',
              color_continuous_scale='Blues')
st.plotly_chart(fig1)

# График 2: Распределение прибыли по всем заказчикам
st.subheader("Распределение прибыли среди заказчиков")
fig2 = px.histogram(profit_by_customer, 
                    x='netsalesamount', 
                    nbins=30, 
                    title='Распределение чистой прибыли среди заказчиков',
                    labels={'netsalesamount': 'Чистая прибыль'})
st.plotly_chart(fig2)

# Группировка по месяцам и топ-5 заказчиков
top_5_customers = profit_by_customer.head(5)['name']
filtered_top_5 = filtered_data[filtered_data['name'].isin(top_5_customers)]
filtered_top_5['order_month'] = pd.to_datetime(filtered_top_5['orderdate']).dt.to_period('M')
monthly_profit = filtered_top_5.groupby(['order_month', 'name'])['netsalesamount'].sum().reset_index()

# График 3: Прибыль по месяцам для топ-5 заказчиков
st.subheader("Прибыль по месяцам для топ-5 заказчиков")
fig3 = px.line(monthly_profit, 
               x='order_month', 
               y='netsalesamount', 
               color='name', 
               markers=True, 
               title='Прибыль по месяцам для топ-5 заказчиков',
               labels={'order_month': 'Месяц', 'netsalesamount': 'Чистая прибыль'})
fig3.update_xaxes(tickformat="%Y-%m")
st.plotly_chart(fig3)

# График 4: Сумма продаж по месяцам для топ-5 заказчиков
st.subheader("Сумма продаж по месяцам для топ-5 заказчиков")
fig4 = px.line(monthly_profit, 
               x='order_month', 
               y='netsalesamount', 
               color='name', 
               markers=True, 
               title='Сумма продаж по месяцам для топ-5 заказчиков',
               labels={'order_month': 'Месяц', 'netsalesamount': 'Сумма продаж'})
fig4.update_xaxes(tickformat="%Y-%m")
st.plotly_chart(fig4)
