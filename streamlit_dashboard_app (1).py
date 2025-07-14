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

# Выбор года для анализа
selected_year = st.selectbox(
    "Выберите год для анализа менеджеров:",
    sorted(fact_with_employeename['year'].unique())
)

# Фильтруем данные по выбранному году
year_data = fact_with_employeename[fact_with_employeename['year'] == selected_year]

# Группируем данные по менеджерам для выбранного года
manager_stats = year_data.groupby('employeename').agg(
    total_sales=('grosssalesamount', 'sum'),
    avg_discount=('discount', 'mean'),  # Используем столбец 'discount'
    order_count=('orderid', 'nunique')
).reset_index()

# Создаем scatter plot для анализа скидки и объема продаж
fig_discount_analysis = px.scatter(
    manager_stats,
    x='avg_discount',
    y='total_sales',
    size='order_count',
    color='employeename',
    hover_name='employeename',
    hover_data=['avg_discount', 'total_sales', 'order_count'],
    title=f"Зависимость объема продаж от среднего размера скидки за {selected_year}",
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

# Отображаем график
st.plotly_chart(fig_discount_analysis)
