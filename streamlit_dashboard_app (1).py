import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Настройка страницы
st.set_page_config(layout="wide", page_title="Анализ продаж", page_icon="📊")

# Загрузка данных
@st.cache_data
def load_data():
    fact_table = pd.read_excel('https://raw.githubusercontent.com/Archchfa/test_task/main/fact_table_v2.xlsx')
    products = pd.read_excel('https://raw.githubusercontent.com/Archchfa/test_task/main/products_v2.xlsx')
    staff = pd.read_excel('https://raw.githubusercontent.com/Archchfa/test_task/main/staff_v2.xlsx')
    calendar = pd.read_excel('https://raw.githubusercontent.com/Archchfa/test_task/main/calendar_v2.xlsx')
    cont = pd.read_excel('https://raw.githubusercontent.com/Archchfa/test_task/main/cont_v2.xlsx')
    return fact_table, products, staff, calendar, cont

fact_table, products, staff, calendar, cont = load_data()

# Подготовка данных
@st.cache_data
def prepare_data():
    # Объединение таблиц
    fact_with_category = pd.merge(fact_table, products[['productid', 'categoryname', 'productname']], on='productid', how='left')
    fact_with_full_info = pd.merge(fact_with_category, cont[['name', 'country']], on='name', how='left')
    
    # Добавление года и дня недели
    fact_with_full_info['year'] = pd.to_datetime(fact_with_full_info['orderdate']).dt.year
    fact_with_full_info['day_of_week'] = pd.to_datetime(fact_with_full_info['orderdate']).dt.dayofweek
    fact_with_full_info['month'] = pd.to_datetime(fact_with_full_info['orderdate']).dt.month
    
    # Для анализа менеджеров оставляем 2020 год
    fact_for_managers = fact_with_full_info.copy()
    fact_with_full_info = fact_with_full_info[fact_with_full_info['year'] != 2020]
    
    # Добавляем имена менеджеров
    fact_with_employeename = pd.merge(
        fact_for_managers,
        staff[['employeeid', 'employeename']],
        left_on='employee_id',
        right_on='employeeid',
        how='left'
    )
    
    return fact_with_full_info, fact_with_employeename

fact_with_full_info, fact_with_employeename = prepare_data()

# Заголовок приложения
st.title("📊 Комплексный анализ продаж")
st.markdown("---")

# 1. Анализ пляжной одежды
st.header("1. Анализ товаров категории 'Пляжная одежда'")
beachwear_data = fact_with_full_info[fact_with_full_info['categoryname'] == 'Пляжная одежда']

# Топ товаров по прибыльности
product_profit = beachwear_data.groupby('productname').agg(
    profit=('netsalesamount', 'sum'),
    sales=('orderid', 'count'),
    avg_price=('unitprice', 'mean')
).reset_index().sort_values('profit', ascending=False)

top_products = product_profit.head(10)

col1, col2 = st.columns(2)
with col1:
    fig1 = px.bar(top_products, x='productname', y='profit', 
                 title='Топ-10 самых прибыльных товаров',
                 labels={'productname': 'Товар', 'profit': 'Прибыль'},
                 color='profit')
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    fig2 = px.pie(top_products, names='productname', values='profit',
                 title='Доля в общей прибыли',
                 hole=0.3)
    st.plotly_chart(fig2, use_container_width=True)

# Топ товаров по количеству продаж
top_selling = product_profit.sort_values('sales', ascending=False).head(10)

col3, col4 = st.columns(2)
with col3:
    fig3 = px.bar(top_selling, x='productname', y='sales',
                 title='Топ-10 самых продаваемых товаров',
                 labels={'productname': 'Товар', 'sales': 'Количество продаж'},
                 color='sales')
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    fig4 = px.scatter(product_profit.head(20), x='sales', y='profit',
                     size='avg_price', color='productname',
                     title='Соотношение продаж и прибыли',
                     labels={'sales': 'Количество продаж', 'profit': 'Прибыль', 'avg_price': 'Средняя цена'},
                     hover_name='productname')
    st.plotly_chart(fig4, use_container_width=True)

# Анализ по странам
st.subheader("Распределение по странам")
country_stats = beachwear_data.groupby('country').agg(
    total_profit=('netsalesamount', 'sum'),
    sales_count=('orderid', 'count')
).reset_index().sort_values('total_profit', ascending=False)

fig5 = px.bar(country_stats, x='country', y='total_profit',
              title='Прибыль от пляжной одежды по странам',
              labels={'country': 'Страна', 'total_profit': 'Прибыль'},
              color='total_profit')
st.plotly_chart(fig5, use_container_width=True)

# 2. Анализ женской обуви в США
st.header("2. Анализ женской обуви в США")
st.markdown("---")

filtered_data_us = fact_with_full_info[
    (fact_with_full_info['categoryname'] == 'Женская обувь') & 
    (fact_with_full_info['country'] == 'Соединённые Штаты Америки')
]

profit_by_customer_us = filtered_data_us.groupby('name')['netsalesamount'].sum().reset_index()
total_profit_us = profit_by_customer_us['netsalesamount'].sum()
profit_by_customer_us['profit_percentage'] = (profit_by_customer_us['netsalesamount'] / total_profit_us) * 100
profit_by_customer_us = profit_by_customer_us.sort_values('netsalesamount', ascending=False)

col5, col6 = st.columns(2)
with col5:
    fig6 = px.bar(profit_by_customer_us.head(10), x='name', y='netsalesamount',
                 title='Наиболее прибыльные магазины',
                 labels={'name': 'Магазин', 'netsalesamount': 'Прибыль'},
                 color='netsalesamount')
    st.plotly_chart(fig6, use_container_width=True)

with col6:
    fig7 = px.pie(profit_by_customer_us.head(10), names='name', values='profit_percentage',
                 title='Процент прибыли каждого магазина',
                 hole=0.3)
    st.plotly_chart(fig7, use_container_width=True)

# 3. Анализ 20% заказчиков в Бразилии
st.header("3. Анализ заказчиков в Бразилии")
st.markdown("---")

filtered_data_br = fact_with_full_info[fact_with_full_info['country'] == 'Бразилия']
profit_by_customer_br = filtered_data_br.groupby('name')['netsalesamount'].sum().reset_index()
total_profit_br = profit_by_customer_br['netsalesamount'].sum()
profit_by_customer_br['profit_percentage'] = (profit_by_customer_br['netsalesamount'] / total_profit_br) * 100
profit_by_customer_br = profit_by_customer_br.sort_values('netsalesamount', ascending=False)
profit_by_customer_br['cumulative_percent'] = profit_by_customer_br['netsalesamount'].cumsum() / total_profit_br * 100

col7, col8, col9 = st.columns(3)
with col7:
    fig8 = px.line(profit_by_customer_br, x='name', y='cumulative_percent',
                  title='Кумулятивная прибыль заказчиков',
                  labels={'name': 'Заказчик', 'cumulative_percent': 'Кумулятивный процент прибыли'},
                  markers=True)
    st.plotly_chart(fig8, use_container_width=True)

with col8:
    top_80 = profit_by_customer_br[profit_by_customer_br['cumulative_percent'] <= 80]
    fig9 = px.bar(top_80, x='name', y='netsalesamount',
                 title='Топ заказчиков (80% прибыли)',
                 labels={'name': 'Заказчик', 'netsalesamount': 'Прибыль'})
    st.plotly_chart(fig9, use_container_width=True)

with col9:
    fig10 = px.pie(profit_by_customer_br.head(10), names='name', values='profit_percentage',
                  title='Процент прибыли',
                  hole=0.3)
    st.plotly_chart(fig10, use_container_width=True)

# 4. Анализ по странам
st.header("4. Сравнение стран")
st.markdown("---")

profit_by_country_year = fact_with_full_info.groupby(['country', 'year'])['grosssalesamount'].sum().reset_index()
profit_type = st.radio("Тип данных:", ('Прибыль', 'Процент прибыли'), horizontal=True)

if profit_type == 'Прибыль':
    fig11 = px.line(profit_by_country_year, x='year', y='grosssalesamount', color='country',
                  title='Динамика прибыли по странам',
                  labels={'year': 'Год', 'grosssalesamount': 'Прибыль', 'country': 'Страна'})
else:
    profit_by_country_year['profit_percentage'] = profit_by_country_year.groupby('year')['grosssalesamount'].transform(
        lambda x: x / x.sum() * 100)
    fig11 = px.line(profit_by_country_year, x='year', y='profit_percentage', color='country',
                  title='Доля прибыли по странам',
                  labels={'year': 'Год', 'profit_percentage': 'Доля прибыли (%)', 'country': 'Страна'})

st.plotly_chart(fig11, use_container_width=True)

# 5. Анализ менеджеров
st.header("5. Эффективность менеджеров")
st.markdown("---")

selected_year = st.selectbox(
    "Выберите год для анализа:",
    sorted(fact_with_employeename['year'].unique()),
    key='manager_year'
)

# Графики в одной строке
col10, col11 = st.columns(2)

with col10:
    year_data = fact_with_employeename[fact_with_employeename['year'] == selected_year]
    manager_percent = year_data.groupby('employeename')['grosssalesamount'].sum().reset_index()
    manager_percent['percentage'] = manager_percent['grosssalesamount'] / manager_percent['grosssalesamount'].sum() * 100
    
    fig12 = px.pie(manager_percent, names='employeename', values='percentage',
                  title=f'Распределение продаж менеджеров ({selected_year} год)',
                  hole=0.3)
    st.plotly_chart(fig12, use_container_width=True)

with col11:
    manager_stats = year_data.groupby('employeename').agg(
        total_sales=('grosssalesamount', 'sum'),
        avg_discount=('discount', 'mean'),
        order_count=('orderid', 'nunique')
    ).reset_index()

    fig13 = px.scatter(manager_stats, x='avg_discount', y='total_sales',
                      size='order_count', color='employeename',
                      title=f'Эффективность менеджеров ({selected_year} год)',
                      labels={'avg_discount': 'Средняя скидка (%)', 
                             'total_sales': 'Объем продаж',
                             'order_count': 'Количество заказов',
                             'employeename': 'Менеджер'},
                      hover_name='employeename')
    
    # Добавляем медианные линии
    median_discount = manager_stats['avg_discount'].median()
    median_sales = manager_stats['total_sales'].median()
    
    fig13.update_layout(
        shapes=[
            dict(type='line', x0=median_discount, y0=0, x1=median_discount, 
                 y1=manager_stats['total_sales'].max(), line=dict(color='red', dash='dash')),
            dict(type='line', x0=0, y0=median_sales, x1=manager_stats['avg_discount'].max(), 
                 y1=median_sales, line=dict(color='red', dash='dash'))
        ]
    )
    st.plotly_chart(fig13, use_container_width=True)

# 6. Анализ дней недели
st.header("6. Анализ продаж по дням недели")
st.markdown("---")

weekday_data = fact_with_full_info.copy()
weekday_data['day_name'] = pd.to_datetime(weekday_data['orderdate']).dt.day_name(locale='ru')
weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
weekday_mapping = {
    'Monday': 'Понедельник',
    'Tuesday': 'Вторник',
    'Wednesday': 'Среда',
    'Thursday': 'Четверг',
    'Friday': 'Пятница',
    'Saturday': 'Суббота',
    'Sunday': 'Воскресенье'
}
weekday_data['day_name'] = weekday_data['day_name'].map(weekday_mapping)
sales_by_weekday = weekday_data.groupby('day_name')['grosssalesamount'].sum().reset_index()

fig14 = px.bar(sales_by_weekday, x='day_name', y='grosssalesamount',
              title='Продажи по дням недели',
              labels={'day_name': 'День недели', 'grosssalesamount': 'Объем продаж'},
              color='grosssalesamount')
st.plotly_chart(fig14, use_container_width=True)

# Выводы
st.header("🔍 Ключевые выводы")
st.markdown("---")

st.subheader("По пляжной одежде:")
top1 = product_profit.iloc[0]
st.write(f"""
- Самый прибыльный товар: **{top1['productname']}** (прибыль: {top1['profit']:,.0f})
- Самый популярный товар: **{product_profit.sort_values('sales', ascending=False).iloc[0]['productname']}** ({product_profit.sort_values('sales', ascending=False).iloc[0]['sales']} продаж)
- Лучшие рынки сбыта: **{country_stats.iloc[0]['country']}** и **{country_stats.iloc[1]['country']}**
""")

st.subheader("По менеджерам:")
best_manager = manager_stats.loc[manager_stats['total_sales'].idxmax()]
st.write(f"""
- Лучший менеджер {selected_year} года: **{best_manager['employeename']}** (продажи: {best_manager['total_sales']:,.0f})
- Средний размер скидки у топ-менеджеров: {manager_stats['avg_discount'].mean():.1f}%
""")

st.subheader("По дням недели:")
best_day = sales_by_weekday.loc[sales_by_weekday['grosssalesamount'].idxmax()]
st.write(f"""
- Самый продаваемый день недели: **{best_day['day_name']}** (объем продаж: {best_day['grosssalesamount']:,.0f})
""")
