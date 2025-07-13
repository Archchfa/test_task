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

# Сумма всей прибыли в выбранной категории и стране
total_profit = profit_by_customer['netsalesamount'].sum()

# Рассчитываем процент прибыли для каждого магазина
profit_by_customer['profit_percentage'] = (profit_by_customer['netsalesamount'] / total_profit) * 100

# Сортируем по прибыли (чистая прибыль)
profit_by_customer = profit_by_customer.sort_values(by='netsalesamount', ascending=False)

# Заголовок страницы
st.title("Тестовое задание")

# Подзаголовок
st.subheader("Какие заказчики наиболее прибыльны в товарной категории «женская обувь» в США?")

# Размещаем два графика в строку
col1, col2 = st.columns(2)

# График 1: Наиболее прибыльные магазины
with col1:
    st.subheader("Наиболее прибыльные магазины")
    fig1 = px.bar(profit_by_customer, 
                  x='name', 
                  y='netsalesamount', 
                  orientation='v',  # Вертикальная ориентация (по оси X магазины)
                  title="Наиболее прибыльные магазины",
                  labels={'netsalesamount': 'Чистая прибыль', 'name': 'Заказчик'})
    
    # Растягиваем график на весь экран
    fig1.update_layout(
        autosize=True,
        width=700,  # увеличиваем ширину
        height=500,  # увеличиваем высоту
        margin=dict(l=0, r=0, t=30, b=0)  # уменьшаем поля для увеличения области графика
    )

    # Поворот оси X, чтобы названия магазинов не накладывались
    fig1.update_xaxes(tickangle=45)

    # Отображение графика
    st.plotly_chart(fig1)

# График 2: Круговая диаграмма с процентом прибыли каждого магазина
with col2:
    st.subheader("Процент прибыли каждого магазина")
    fig2 = px.pie(profit_by_customer, 
                  names='name', 
                  values='profit_percentage',  # Используем процент прибыли
                  title="Процент прибыли каждого магазина",
                  labels={'profit_percentage': 'Процент прибыли', 'name': 'Заказчик'})
    
    # Отображение графика
    st.plotly_chart(fig2)

# Подзаголовок для 3, 4 и 5 графиков
st.subheader("Какие 20% заказчиков приносят 80% прибыли компании в Бразилии?")

# Размещаем 3 графика в строку
col3, col4, col5 = st.columns(3)

# Фильтруем данные для Бразилии
filtered_data_br = fact_with_full_info[fact_with_full_info['country'] == 'Бразилия']

# Агрегируем прибыль по заказчикам для Бразилии
profit_by_customer_br = filtered_data_br.groupby('name')['netsalesamount'].sum().reset_index()

# Сумма всей прибыли в Бразилии
total_profit_br = profit_by_customer_br['netsalesamount'].sum()

# Рассчитываем процент прибыли для каждого магазина в Бразилии
profit_by_customer_br['profit_percentage'] = (profit_by_customer_br['netsalesamount'] / total_profit_br) * 100

# График 3: Кумулятивная прибыль (линейный график) с точками для Бразилии
with col3:
    st.subheader("Кумулятивная прибыль")
    profit_by_customer_br['cumulative_profit'] = profit_by_customer_br['netsalesamount'].cumsum()
    profit_by_customer_br['cumulative_percent'] = (profit_by_customer_br['cumulative_profit'] / total_profit_br) * 100
    
    fig3 = px.line(profit_by_customer_br, 
                   x='name', 
                   y='cumulative_percent', 
                   title="Кумулятивная прибыль заказчиков (Бразилия)",
                   labels={'cumulative_percent': 'Кумулятивный процент прибыли', 'name': 'Заказчик'},
                   markers=True)  # Добавляем маркеры (точки)
    
    # Растягиваем график на весь экран
    fig3.update_layout(
        autosize=True,
        width=700,
        height=500,
        margin=dict(l=0, r=0, t=30, b=0)
    )
    
    fig3.update_xaxes(tickangle=45)
    
    # Отображаем график
    st.plotly_chart(fig3)

# График 4: Диаграмма рассеяния (scatter plot) для Бразилии
with col4:
    st.subheader("Диаграмма рассеяния: Прибыль по заказчикам (Бразилия)")
    fig4 = px.scatter(profit_by_customer_br, 
                      x='name', 
                      y='netsalesamount', 
                      title="Прибыль по заказчикам (Бразилия)",
                      labels={'netsalesamount': 'Чистая прибыль', 'name': 'Заказчик'})
    
    # Отображение графика
    st.plotly_chart(fig4)

# График 5: Круговая диаграмма с процентом прибыли каждого магазина для Бразилии
with col5:
    st.subheader("Процент прибыли каждого магазина (Бразилия)")
    fig5 = px.pie(profit_by_customer_br, 
                  names='name', 
                  values='profit_percentage',  # Используем процент прибыли
                  title="Процент прибыли каждого магазина (Бразилия)",
                  labels={'profit_percentage': 'Процент прибыли', 'name': 'Заказчик'})
    
    # Отображение графика
    st.plotly_chart(fig5)
