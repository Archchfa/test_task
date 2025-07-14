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

# Фильтруем данные по категории "Женская обувь" и стране "Соединённые Штаты Америки" (для 1 и 2 графиков)
filtered_data_us = fact_with_full_info[
    (fact_with_full_info['categoryname'] == 'Женская обувь') & 
    (fact_with_full_info['country'] == 'Соединённые Штаты Америки')
]

# Агрегируем прибыль по заказчикам для США
profit_by_customer_us = filtered_data_us.groupby('name')['netsalesamount'].sum().reset_index()

# Сумма всей прибыли в выбранной категории и стране для США
total_profit_us = profit_by_customer_us['netsalesamount'].sum()

# Рассчитываем процент прибыли для каждого магазина для США
profit_by_customer_us['profit_percentage'] = (profit_by_customer_us['netsalesamount'] / total_profit_us) * 100

# Сортируем по прибыли (чистая прибыль) для США
profit_by_customer_us = profit_by_customer_us.sort_values(by='netsalesamount', ascending=False)


# Для 3, 4 и 5 графиков: фильтруем данные для Бразилии (все магазины из Бразилии)
filtered_data_br = fact_with_full_info[
    (fact_with_full_info['country'] == 'Бразилия')
]

# Агрегируем прибыль по заказчикам для Бразилии
profit_by_customer_br = filtered_data_br.groupby('name')['netsalesamount'].sum().reset_index()

# Сумма всей прибыли в выбранной категории и стране для Бразилии
total_profit_br = profit_by_customer_br['netsalesamount'].sum()

# Рассчитываем процент прибыли для каждого магазина для Бразилии
profit_by_customer_br['profit_percentage'] = (profit_by_customer_br['netsalesamount'] / total_profit_br) * 100

# Сортируем по прибыли (чистая прибыль) для Бразилии
profit_by_customer_br = profit_by_customer_br.sort_values(by='netsalesamount', ascending=False)

# Кумулятивная прибыль для Бразилии
profit_by_customer_br['cumulative_profit'] = profit_by_customer_br['netsalesamount'].cumsum()

# Кумулятивный процент для Бразилии
profit_by_customer_br['cumulative_percent'] = (profit_by_customer_br['cumulative_profit'] / total_profit_br) * 100


# Добавляем год в данные
fact_with_full_info['year'] = pd.to_datetime(fact_with_full_info['orderdate']).dt.year

# Исключаем 2020 год
fact_with_full_info = fact_with_full_info[fact_with_full_info['year'] != 2020]

# Объединяем данные с таблицей staff для получения имен менеджеров
fact_with_full_info_with_names = pd.merge(
    fact_with_full_info, 
    staff[['employeeid', 'employeename']],  # Убедитесь, что используете employeeid и employeename
    left_on='employee_id',
    right_on='employeeid',
    how='left'
)

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
                  orientation='v',  # Вертикальная ориентация (по оси X магазины)
                  title="Наиболее прибыльные магазины (США)",
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

# График 2: Круговая диаграмма с процентом прибыли каждого магазина для США
with col2:
    st.subheader("Процент прибыли каждого магазина (США)")
    fig2 = px.pie(profit_by_customer_us, 
                  names='name', 
                  values='profit_percentage',  # Используем процент прибыли
                  title="Процент прибыли каждого магазина (США)",
                  labels={'profit_percentage': 'Процент прибыли', 'name': 'Заказчик'})
    
    # Отображение графика
    st.plotly_chart(fig2)


# Подзаголовок для 3, 4 и 5 графиков
st.subheader("Какие 20% заказчиков приносят 80% прибыли компании в Бразилии?")

# Размещаем 3 графика в строку
col3, col4, col5 = st.columns(3)

# График 3: Кумулятивная прибыль (линейный график) с точками для Бразилии
with col3:
    st.subheader("Кумулятивная прибыль")
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

# График 4: Столбчатая диаграмма с прибыльностью по заказчикам для Бразилии (только 80% прибыли)
with col4:
    st.subheader("Прибыль по заказчикам (Бразилия) с 80% прибыли")
    # Выбираем 80% заказчиков, которые составляют 80% прибыли
    top_80_percent_customers = profit_by_customer_br[profit_by_customer_br['cumulative_percent'] <= 80]
    
    fig4 = px.bar(top_80_percent_customers, 
                  x='name', 
                  y='netsalesamount', 
                  title="Прибыль по заказчикам (Бразилия) с 80% прибыли",
                  labels={'netsalesamount': 'Чистая прибыль', 'name': 'Заказчик'})

    # Растягиваем график на весь экран
    fig4.update_layout(
        autosize=True,
        width=700,
        height=500,
        margin=dict(l=0, r=0, t=30, b=0)
    )

    fig4.update_xaxes(tickangle=45)

    # Отображаем график
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


# Дополнение: График 6 - Сумма прибыли для каждой страны по годам (по grosssalesamount)
st.subheader("Сумма прибыли для каждой страны по годам (по grosssalesamount)")

# Группируем данные по странам и годам с использованием grosssalesamount
profit_by_country_year = fact_with_full_info.groupby(['country', 'year'])['grosssalesamount'].sum().reset_index()

# Добавляем переключатель между Прибылью и Процентом прибыли
profit_type = st.radio("Выберите тип данных для отображения:", ('Прибыль', 'Процент прибыли'))

if profit_type == 'Прибыль':
    fig6 = px.line(profit_by_country_year, 
                   x='year', 
                   y='grosssalesamount', 
                   color='country', 
                   title="Сумма прибыли по странам и годам (по grosssalesamount)",
                   labels={'grosssalesamount': 'Сумма прибыли', 'year': 'Год', 'country': 'Страна'})
else:
    # Рассчитываем процент прибыли для каждой страны
    total_profit_per_year = profit_by_country_year.groupby('year')['grosssalesamount'].transform('sum')
    profit_by_country_year['profit_percentage'] = (profit_by_country_year['grosssalesamount'] / total_profit_per_year) * 100
    fig6 = px.line(profit_by_country_year, 
                   x='year', 
                   y='profit_percentage', 
                   color='country', 
                   title="Процент прибыли по странам и годам (по grosssalesamount)",
                   labels={'profit_percentage': 'Процент прибыли', 'year': 'Год', 'country': 'Страна'})

st.plotly_chart(fig6)


# Дополнение: График 7 - Количество заказов по странам и годам (Столбчатая диаграмма)
st.subheader("Количество заказов по странам и годам")

# Группируем данные по странам и годам, считая количество заказов
orders_by_country_year = fact_with_full_info.groupby(['country', 'year'])['orderid'].nunique().reset_index()

# Столбчатая диаграмма
fig7 = px.bar(orders_by_country_year, 
              x='year', 
              y='orderid', 
              color='country', 
              title="Количество заказов по странам и годам",
              labels={'orderid': 'Количество заказов', 'year': 'Год', 'country': 'Страна'})

st.plotly_chart(fig7)

# Подзаголовок для графика по менеджерам
st.subheader("Какой из менеджеров дает компании наибольший объем продаж?")

# Столбчатая диаграмма с группировкой (столбцы рядом)
fig_employee_sales = px.bar(
    fact_with_full_info_with_names.groupby(['employeename', 'year'])['grosssalesamount'].sum().reset_index(), 
    x='year', 
    y='grosssalesamount', 
    color='employeename',  # Используем имена вместо ID
    barmode='group',  # Столбцы рядом, а не наложение
    title="Сумма Gross Sales по менеджерам по годам",
    labels={
        'grosssalesamount': 'Сумма grosssalesamount', 
        'year': 'Год', 
        'employeename': 'Менеджер'
    },
    category_orders={"year": sorted(fact_with_full_info_with_names['year'].unique())}  # Сортировка годов
)

# Настраиваем размер графика
fig_employee_sales.update_layout(
    height=500,
    width=900,
    margin=dict(l=50, r=50, t=80, b=100),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.3,
        xanchor="center",
        x=0.5
    )
)

# Отображаем график
st.plotly_chart(fig_employee_sales)

# Подзаголовок для графика с выбором года
st.subheader("Распределение продаж между менеджерами по годам")

# Выбор года для анализа
selected_year = st.selectbox(
    "Выберите год для отображения процента продаж:", 
    sorted(fact_with_full_info_with_names['year'].unique())
)

# Фильтруем данные по выбранному году
fact_with_full_info_selected_year = fact_with_full_info_with_names[
    fact_with_full_info_with_names['year'] == selected_year
]

# Агрегируем данные по сотрудникам за выбранный год
sales_by_employeename_selected_year = fact_with_full_info_selected_year.groupby(
    'employeename'
)['grosssalesamount'].sum().reset_index()

# Рассчитываем проценты для каждого сотрудника
total_sales_selected_year = sales_by_employeename_selected_year['grosssalesamount'].sum()
sales_by_employeename_selected_year['sales_percentage'] = (
    sales_by_employeename_selected_year['grosssalesamount'] / total_sales_selected_year
) * 100

# Круговая диаграмма для процента продаж каждого сотрудника
fig_pie_employee_sales = px.pie(
    sales_by_employeename_selected_year, 
    names='employeename', 
    values='sales_percentage', 
    title=f"Процент продаж менеджеров за {selected_year}",
    labels={'sales_percentage': 'Процент продаж', 'employeename': 'Менеджер'}
)

# Отображаем круговую диаграмму
st.plotly_chart(fig_pie_employee_sales)
