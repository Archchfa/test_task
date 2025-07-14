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

# Добавляем год в данные
fact_with_full_info['year'] = pd.to_datetime(fact_with_full_info['orderdate']).dt.year

# Создаем копию данных с 2020 годом для анализа менеджеров
fact_for_managers = fact_with_full_info.copy()

# Исключаем 2020 год для всех графиков, кроме анализа менеджеров
fact_with_full_info = fact_with_full_info[fact_with_full_info['year'] != 2020]

# Объединяем с данными о сотрудниках для анализа менеджеров (включая 2020 год)
fact_with_employeename = pd.merge(
    fact_for_managers,
    staff[['employeeid', 'employeename']],
    left_on='employee_id',
    right_on='employeeid',
    how='left'
)

# Фильтруем данные по категории "Женская обувь" и стране "Соединённые Штаты Америки"
filtered_data_us = fact_with_full_info[
    (fact_with_full_info['categoryname'] == 'Женская обувь') & 
    (fact_with_full_info['country'] == 'Соединённые Штаты Америки')
]

# Агрегируем прибыль по заказчикам для США
profit_by_customer_us = filtered_data_us.groupby('name')['netsalesamount'].sum().reset_index()
total_profit_us = profit_by_customer_us['netsalesamount'].sum()
profit_by_customer_us['profit_percentage'] = (profit_by_customer_us['netsalesamount'] / total_profit_us) * 100
profit_by_customer_us = profit_by_customer_us.sort_values(by='netsalesamount', ascending=False)

# Фильтруем данные для Бразилии
filtered_data_br = fact_with_full_info[(fact_with_full_info['country'] == 'Бразилия')]

# Агрегируем прибыль по заказчикам для Бразилии
profit_by_customer_br = filtered_data_br.groupby('name')['netsalesamount'].sum().reset_index()
total_profit_br = profit_by_customer_br['netsalesamount'].sum()
profit_by_customer_br['profit_percentage'] = (profit_by_customer_br['netsalesamount'] / total_profit_br) * 100
profit_by_customer_br = profit_by_customer_br.sort_values(by='netsalesamount', ascending=False)
profit_by_customer_br['cumulative_profit'] = profit_by_customer_br['netsalesamount'].cumsum()
profit_by_customer_br['cumulative_percent'] = (profit_by_customer_br['cumulative_profit'] / total_profit_br) * 100

# Заголовок страницы
st.title("Тестовое задание")

# Подзаголовок для США
st.subheader("Какие заказчики наиболее прибыльны в товарной категории «женская обувь» в США?")

# Размещаем 1 и 2 графики в строку
col1, col2 = st.columns(2)

# График 1: Наиболее прибыльные магазины для США
with col1:
    st.subheader("Наиболее прибыльные магазины")
    fig1 = px.bar(profit_by_customer_us, 
                 x='name', 
                 y='netsalesamount',
                 title="Наиболее прибыльные магазины (США)",
                 labels={'netsalesamount': 'Чистая прибыль', 'name': 'Заказчик'})
    fig1.update_layout(width=700, height=500)
    st.plotly_chart(fig1)

# График 2: Круговая диаграмма с процентом прибыли каждого магазина для США
with col2:
    st.subheader("Процент прибыли каждого магазина (США)")
    fig2 = px.pie(profit_by_customer_us,
                 names='name',
                 values='profit_percentage',
                 title="Процент прибыли каждого магазина (США)")
    st.plotly_chart(fig2)

# Подзаголовок для Бразилии
st.subheader("Какие 20% заказчиков приносят 80% прибыли компании в Бразилии?")

# Размещаем 3 графика в строку
col3, col4, col5 = st.columns(3)

# График 3: Кумулятивная прибыль для Бразилии
with col3:
    st.subheader("Кумулятивная прибыль")
    fig3 = px.line(profit_by_customer_br,
                  x='name',
                  y='cumulative_percent',
                  title="Кумулятивная прибыль заказчиков (Бразилия)",
                  markers=True)
    fig3.update_layout(width=700, height=500)
    st.plotly_chart(fig3)

# График 4: Топ 80% прибыли для Бразилии
with col4:
    st.subheader("Прибыль по заказчикам (80% прибыли)")
    top_80 = profit_by_customer_br[profit_by_customer_br['cumulative_percent'] <= 80]
    fig4 = px.bar(top_80,
                 x='name',
                 y='netsalesamount',
                 title="Прибыль по заказчикам (80% прибыли)")
    fig4.update_layout(width=700, height=500)
    st.plotly_chart(fig4)

# График 5: Круговая диаграмма для Бразилии
with col5:
    st.subheader("Процент прибыли (Бразилия)")
    fig5 = px.pie(profit_by_customer_br,
                 names='name',
                 values='profit_percentage',
                 title="Процент прибыли (Бразилия)")
    st.plotly_chart(fig5)

# График 6: Прибыль по странам и годам
st.subheader("Сумма прибыли для каждой страны по годам")
profit_by_country_year = fact_with_full_info.groupby(['country', 'year'])['grosssalesamount'].sum().reset_index()
profit_type = st.radio("Тип данных:", ('Прибыль', 'Процент прибыли'))

if profit_type == 'Прибыль':
    fig6 = px.line(profit_by_country_year,
                  x='year',
                  y='grosssalesamount',
                  color='country',
                  title="Сумма прибыли по странам и годам")
else:
    profit_by_country_year['profit_percentage'] = profit_by_country_year.groupby('year')['grosssalesamount'].apply(
        lambda x: x / x.sum() * 100)
    fig6 = px.line(profit_by_country_year,
                  x='year',
                  y='profit_percentage',
                  color='country',
                  title="Процент прибыли по странам и годам")
st.plotly_chart(fig6)

# График 7: Количество заказов по странам и годам
st.subheader("Количество заказов по странам и годам")
orders_by_country_year = fact_with_full_info.groupby(['country', 'year'])['orderid'].nunique().reset_index()
fig7 = px.bar(orders_by_country_year,
             x='year',
             y='orderid',
             color='country',
             title="Количество заказов по странам и годам")
st.plotly_chart(fig7)

# Анализ менеджеров (включая 2020 год)
st.subheader("Анализ продаж менеджеров (включая 2020 год)")

# График продаж по менеджерам по годам
manager_sales = fact_with_employeename.groupby(['employeename', 'year'])['grosssalesamount'].sum().reset_index()
fig_manager = px.bar(manager_sales,
                    x='year',
                    y='grosssalesamount',
                    color='employeename',
                    barmode='group',
                    title="Продажи по менеджерам по годам")
fig_manager.update_layout(height=500, width=900)
st.plotly_chart(fig_manager)

# Круговая диаграмма по выбранному году
selected_year = st.selectbox(
    "Выберите год для анализа менеджеров:",
    sorted(fact_with_employeename['year'].unique())
)

year_data = fact_with_employeename[fact_with_employeename['year'] == selected_year]
manager_percent = year_data.groupby('employeename')['grosssalesamount'].sum().reset_index()
manager_percent['percentage'] = manager_percent['grosssalesamount'] / manager_percent['grosssalesamount'].sum() * 100

fig_pie = px.pie(manager_percent,
                names='employeename',
                values='percentage',
                title=f"Распределение продаж менеджеров за {selected_year} год")
st.plotly_chart(fig_pie)

# Новый анализ: зависимость объема продаж от среднего размера скидки
st.subheader("Зависимость объема продаж от среднего размера скидки")

# Группируем данные по менеджерам
manager_stats = fact_with_employeename.groupby('employeename').agg(
    total_sales=('grosssalesamount', 'sum'),
    avg_discount=('discount', 'mean'),
    order_count=('orderid', 'nunique')
).reset_index()

# Создаем scatter plot
fig_discount_analysis = px.scatter(
    manager_stats,
    x='avg_discount',
    y='total_sales',
    size='order_count',
    color='employeename',
    hover_name='employeename',
    hover_data=['avg_discount', 'total_sales', 'order_count'],
    title="Зависимость объема продаж от среднего размера скидки",
    labels={
        'avg_discount': 'Средний размер скидки (%)',
        'total_sales': 'Общий объем продаж',
        'order_count': 'Количество заказов',
        'employeename': 'Менеджер'
    }
)

# Добавляем линии для медианных значений
median_discount = manager_stats['avg_discount'].median()
median_sales = manager_stats['total_sales'].median()

fig_discount_analysis.update_layout(
    shapes=[
        # Вертикальная линия (медианная скидка)
        dict(
            type='line',
            x0=median_discount,
            y0=0,
            x1=median_discount,
            y1=manager_stats['total_sales'].max(),
            line=dict(color='red', dash='dash')
        ),
        # Горизонтальная линия (медианные продажи)
        dict(
            type='line',
            x0=0,
            y0=median_sales,
            x1=manager_stats['avg_discount'].max(),
            y1=median_sales,
            line=dict(color='red', dash='dash')
        )
    ],
    annotations=[
        dict(
            x=median_discount,
            y=manager_stats['total_sales'].max(),
            xref='x',
            yref='y',
            text='Средняя скидка',
            showarrow=True,
            arrowhead=1,
            ax=-40,
            ay=-40
        ),
        dict(
            x=manager_stats['avg_discount'].max(),
            y=median_sales,
            xref='x',
            yref='y',
            text='Средние продажи',
            showarrow=True,
            arrowhead=1,
            ax=40,
            ay=40
        )
    ]
)

st.plotly_chart(fig_discount_analysis)
