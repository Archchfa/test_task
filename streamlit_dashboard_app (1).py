import streamlit as st
import pandas as pd
import plotly.express as px

# Загрузка данных
fact_table_url = 'https://raw.githubusercontent.com/Archchfa/test_task/main/fact_table_v2.xlsx'
products_url = 'https://raw.githubusercontent.com/Archchfa/test_task/main/products_v2.xlsx'
staff_url = 'https://raw.githubusercontent.com/Archchfa/test_task/main/staff_v2.xlsx'
calendar_url = 'https://raw.githubusercontent.com/Archchfa/test_task/main/calendar_v2.xlsx'
cont_url = 'https://raw.githubusercontent.com/Archchfa/test_task/main/cont_v2.xlsx'

fact_with_calendar = pd.read_excel(fact_table_url)
products = pd.read_excel(products_url)
staff = pd.read_excel(staff_url)
calendar = pd.read_excel(calendar_url)
cont = pd.read_excel(cont_url)

# Подготовка данных
fact_with_category = pd.merge(fact_with_calendar, products[['productid', 'categoryname']], on='productid', how='left')
fact_with_full_info = pd.merge(fact_with_category, cont[['name', 'country']], on='name', how='left')
fact_with_full_info['year'] = pd.to_datetime(fact_with_full_info['orderdate']).dt.year
fact_for_managers = fact_with_full_info.copy()
fact_with_full_info = fact_with_full_info[fact_with_full_info['year'] != 2020]

fact_with_employeename = pd.merge(
    fact_for_managers,
    staff[['employeeid', 'employeename']],
    left_on='employee_id',
    right_on='employeeid',
    how='left'
)

# 1. График для США - женская обувь
st.subheader("Какие заказчики наиболее прибыльны в товарной категории «женская обувь» в США?")

filtered_data_us = fact_with_full_info[
    (fact_with_full_info['categoryname'] == 'Женская обувь') & 
    (fact_with_full_info['country'] == 'Соединённые Штаты Америки')
]

profit_by_customer_us = filtered_data_us.groupby('name')['netsalesamount'].sum().reset_index()
total_profit_us = profit_by_customer_us['netsalesamount'].sum()
profit_by_customer_us['profit_percentage'] = (profit_by_customer_us['netsalesamount'] / total_profit_us) * 100
profit_by_customer_us = profit_by_customer_us.sort_values(by='netsalesamount', ascending=False)

col1, col2 = st.columns(2)
with col1:
    fig1 = px.bar(profit_by_customer_us, x='name', y='netsalesamount',
                 title="Наиболее прибыльные магазины",
                 labels={'netsalesamount': 'Чистая прибыль', 'name': 'Заказчик'})
    st.plotly_chart(fig1)

with col2:
    fig2 = px.pie(profit_by_customer_us, names='name', values='profit_percentage',
                 title="Процент прибыли каждого магазина")
    st.plotly_chart(fig2)

# 2. График для Бразилии - 20% заказчиков
st.subheader("Какие 20% заказчиков приносят 80% прибыли компании в Бразилии?")

filtered_data_br = fact_with_full_info[(fact_with_full_info['country'] == 'Бразилия')]
profit_by_customer_br = filtered_data_br.groupby('name')['netsalesamount'].sum().reset_index()
total_profit_br = profit_by_customer_br['netsalesamount'].sum()
profit_by_customer_br['profit_percentage'] = (profit_by_customer_br['netsalesamount'] / total_profit_br) * 100
profit_by_customer_br = profit_by_customer_br.sort_values(by='netsalesamount', ascending=False)
profit_by_customer_br['cumulative_profit'] = profit_by_customer_br['netsalesamount'].cumsum()
profit_by_customer_br['cumulative_percent'] = (profit_by_customer_br['cumulative_profit'] / total_profit_br) * 100

col3, col4, col5 = st.columns(3)
with col3:
    fig3 = px.line(profit_by_customer_br, x='name', y='cumulative_percent',
                  title="Кумулятивная прибыль заказчиков", markers=True)
    st.plotly_chart(fig3)

with col4:
    top_80 = profit_by_customer_br[profit_by_customer_br['cumulative_percent'] <= 80]
    fig4 = px.bar(top_80, x='name', y='netsalesamount',
                 title="Прибыль по заказчикам (80% прибыли)")
    st.plotly_chart(fig4)

with col5:
    fig5 = px.pie(profit_by_customer_br, names='name', values='profit_percentage',
                 title="Процент прибыли")
    st.plotly_chart(fig5)

# 3. График по странам
st.subheader("Какие страны наиболее перспективны?")
profit_by_country_year = fact_with_full_info.groupby(['country', 'year'])['grosssalesamount'].sum().reset_index()
profit_type = st.radio("Тип данных:", ('Прибыль', 'Процент прибыли'), key='profit_type')

if profit_type == 'Прибыль':
    fig6 = px.line(profit_by_country_year, x='year', y='grosssalesamount', color='country',
                  title="Динамика прибыли по странам")
else:
    profit_by_country_year['profit_percentage'] = profit_by_country_year.groupby('year')['grosssalesamount'].apply(
        lambda x: x / x.sum() * 100)
    fig6 = px.line(profit_by_country_year, x='year', y='profit_percentage', color='country',
                  title="Доля прибыли по странам")
st.plotly_chart(fig6)

# 4. Количество заказов по странам и годам
orders_by_country_year = fact_with_full_info.groupby(['country', 'year'])['orderid'].nunique().reset_index()
fig7 = px.bar(orders_by_country_year, x='year', y='orderid', color='country',
             title="")
st.plotly_chart(fig7)

# 5. Анализ менеджеров
st.subheader("Анализ продаж менеджеров (включая 2020 год)")

manager_sales = fact_with_employeename.groupby(['employeename', 'year'])['grosssalesamount'].sum().reset_index()
fig_manager = px.bar(manager_sales, x='year', y='grosssalesamount', color='employeename',
                    barmode='group', title="Продажи по менеджерам по годам")
st.plotly_chart(fig_manager)

selected_year = st.selectbox(
    "Выберите год для анализа менеджеров:",
    sorted(fact_with_employeename['year'].unique())
)

# Размещаем графики pie и discount на одном уровне
col_pie, col_discount = st.columns(2)

with col_pie:
    year_data = fact_with_employeename[fact_with_employeename['year'] == selected_year]
    manager_percent = year_data.groupby('employeename')['grosssalesamount'].sum().reset_index()
    manager_percent['percentage'] = manager_percent['grosssalesamount'] / manager_percent['grosssalesamount'].sum() * 100
    fig_pie = px.pie(manager_percent, names='employeename', values='percentage',
                    title=f"Распределение продаж менеджеров за {selected_year} год")
    st.plotly_chart(fig_pie)

with col_discount:
    # График зависимости объема продаж от скидки
    year_data = fact_with_employeename[fact_with_employeename['year'] == selected_year]
    manager_stats = year_data.groupby('employeename').agg(
        total_sales=('grosssalesamount', 'sum'),
        avg_discount=('discount', 'mean'),
        order_count=('orderid', 'nunique')
    ).reset_index()

    fig_discount = px.scatter(
        manager_stats,
        x='avg_discount',
        y='total_sales',
        size='order_count',
        color='employeename',
        hover_name='employeename',
        title=f"Зависимость продаж от скидки за {selected_year} год",
        labels={
            'avg_discount': 'Средний размер скидки (%)',
            'total_sales': 'Объем продаж',
            'order_count': 'Количество заказов'
        }
    )
    
    # Добавляем медианные линии
    median_discount = manager_stats['avg_discount'].median()
    median_sales = manager_stats['total_sales'].median()
    
    fig_discount.update_layout(
        shapes=[
            dict(type='line', x0=median_discount, y0=0, x1=median_discount, 
                 y1=manager_stats['total_sales'].max(), line=dict(color='red', dash='dash')),
            dict(type='line', x0=0, y0=median_sales, x1=manager_stats['avg_discount'].max(), 
                 y1=median_sales, line=dict(color='red', dash='dash'))
        ]
    )
    st.plotly_chart(fig_discount)

# 6. График дней недели для новорожденных
st.subheader("Какие дни недели наиболее продуктивны для продаж товарной категории «Одежда для новорожденных»?")

newborn_data = fact_with_employeename[
    (fact_with_employeename['categoryname'] == 'Одежда для новорожденных') &
    (fact_with_employeename['year'].isin([2019, 2020]))
]

newborn_data['day_of_week'] = pd.to_datetime(newborn_data['orderdate']).dt.dayofweek
weekday_names = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
newborn_data['weekday_name'] = newborn_data['day_of_week'].apply(lambda x: weekday_names[x])

sales_by_weekday = newborn_data.groupby('weekday_name')['grosssalesamount'].sum().reset_index()
sales_by_weekday['weekday_name'] = pd.Categorical(
    sales_by_weekday['weekday_name'],
    categories=weekday_names,
    ordered=True
)
sales_by_weekday = sales_by_weekday.sort_values('weekday_name')

fig_weekday = px.bar(
    sales_by_weekday,
    x='weekday_name',
    y='grosssalesamount',
    title='Продажи одежды для новорожденных по дням недели (2019-2020)',
    labels={'weekday_name': 'День недели', 'grosssalesamount': 'Объем продаж'}
)
st.plotly_chart(fig_weekday)

top_day = sales_by_weekday.loc[sales_by_weekday['grosssalesamount'].idxmax()]
st.write(f"Наиболее продуктивный день недели: **{top_day['weekday_name']}** (объем продаж: {top_day['grosssalesamount']:,.0f})")


# 7. Анализ товаров категории "Пляжная одежда"
st.subheader("Анализ товаров категории «Пляжная одежда»")

try:
    # Фильтруем данные по категории "Пляжная одежда"
    beachwear_data = fact_with_full_info[fact_with_full_info['categoryname'] == 'Пляжная одежда'].copy()
    
    # Проверяем наличие необходимых столбцов
    required_columns = ['productid', 'orderid', 'netsalesamount', 'unitprice']
    missing_columns = [col for col in required_columns if col not in beachwear_data.columns]
    
    if missing_columns:
        st.error(f"Отсутствуют необходимые столбцы в данных: {', '.join(missing_columns)}")
    else:
        # Добавляем названия товаров
        beachwear_data = pd.merge(
            beachwear_data, 
            products[['productid', 'productname']], 
            on='productid', 
            how='left'
        )
        
        # Проверяем наличие столбца productname после объединения
        if 'productname' not in beachwear_data.columns:
            st.error("Не удалось добавить названия товаров - столбец 'productname' отсутствует")
        else:
            # Группируем данные по товарам
            product_stats = beachwear_data.groupby('productname').agg(
                sales_count=('orderid', 'count'),
                total_profit=('netsalesamount', 'sum'),
                avg_price=('unitprice', 'mean')
            ).reset_index().sort_values('total_profit', ascending=False)

            # Топ-10 самых прибыльных товаров
            st.markdown("**Топ-10 самых прибыльных товаров**")
            col_beach1, col_beach2 = st.columns(2)

            with col_beach1:
                fig_beach1 = px.bar(
                    product_stats.head(10),
                    x='productname',
                    y='total_profit',
                    title='Общая прибыль по товарам',
                    labels={'productname': 'Название товара', 'total_profit': 'Прибыль'},
                    color='total_profit'
                )
                st.plotly_chart(fig_beach1, use_container_width=True)

            with col_beach2:
                fig_beach2 = px.pie(
                    product_stats.head(10),
                    names='productname',
                    values='total_profit',
                    title='Доля в общей прибыли',
                    hole=0.3
                )
                st.plotly_chart(fig_beach2, use_container_width=True)

            # Топ-10 самых продаваемых товаров
            st.markdown("**Топ-10 самых продаваемых товаров**")
            col_beach3, col_beach4 = st.columns(2)

            with col_beach3:
                fig_beach3 = px.bar(
                    product_stats.sort_values('sales_count', ascending=False).head(10),
                    x='productname',
                    y='sales_count',
                    title='Количество продаж',
                    labels={'productname': 'Название товара', 'sales_count': 'Количество продаж'},
                    color='sales_count'
                )
                st.plotly_chart(fig_beach3, use_container_width=True)

            with col_beach4:
                fig_beach4 = px.scatter(
                    product_stats.head(20),
                    x='sales_count',
                    y='total_profit',
                    size='avg_price',
                    color='productname',
                    title='Соотношение продаж и прибыли',
                    labels={
                        'sales_count': 'Количество продаж',
                        'total_profit': 'Общая прибыль',
                        'avg_price': 'Средняя цена'
                    },
                    hover_name='productname'
                )
                st.plotly_chart(fig_beach4, use_container_width=True)

            # Анализ по странам для пляжной одежды
            if 'country' in beachwear_data.columns:
                st.markdown("**Распределение продаж по странам**")
                country_stats_beach = beachwear_data.groupby('country').agg(
                    total_profit=('netsalesamount', 'sum'),
                    sales_count=('orderid', 'count')
                ).reset_index()

                fig_beach5 = px.bar(
                    country_stats_beach.sort_values('total_profit', ascending=False),
                    x='country',
                    y='total_profit',
                    title='Прибыль от пляжной одежды по странам',
                    labels={'country': 'Страна', 'total_profit': 'Прибыль'},
                    color='total_profit'
                )
                st.plotly_chart(fig_beach5, use_container_width=True)
            else:
                st.warning("Столбец 'country' отсутствует в данных для анализа по странам")

except Exception as e:
    st.error(f"Произошла ошибка при анализе категории 'Пляжная одежда': {str(e)}")
st.write("Доступные столбцы в данных:", list(fact_with_full_info.columns))
st.write("Доступные столбцы в products:", list(products.columns))
