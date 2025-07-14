import streamlit as st
import pandas as pd
import plotly.express as px

# Загрузка данных
fact_table_url = 'https://raw.githubusercontent.com/Archchfa/test_task/main/fact_table_v2.xlsx'
products_url = 'https://raw.githubusercontent.com/Archchfa/test_task/main/products_v2.xlsx'
staff_url = 'https://raw.githubusercontent.com/Archchfa/test_task/main/staff_v2.xlsx'
calendar_url = 'https://raw.githubusercontent.com/Archchfa/test_task/main/calendar_v2.xlsx'
cont_url = 'https://raw.githubusercontent.com/Archchfa/test_task/main/cont_v2.xlsx'
category_plan_url = 'https://raw.githubusercontent.com/Archchfa/test_task/main/categpry_plan.xlsx'

fact_with_calendar = pd.read_excel(fact_table_url)
products = pd.read_excel(products_url)
staff = pd.read_excel(staff_url)
calendar = pd.read_excel(calendar_url)
cont = pd.read_excel(cont_url)
category_plan = pd.read_excel(category_plan_url)

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

# Добавляем названия товаров к основным данным
fact_with_products = pd.merge(
    fact_with_full_info,
    products[['productid', 'productname']],
    on='productid',
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

# 7. Анализ товара "Костюм для бега"
st.header("Анализ товара «Костюм для бега»")

try:
    # Фильтруем данные по товару
    running_suit_data = fact_with_products[fact_with_products['productname'] == 'Костюм для бега']
    
    if running_suit_data.empty:
        st.warning("Товар 'Костюм для бега' не найден в данных")
    else:
        # Анализ динамики прибыли по годам
        yearly_profit = running_suit_data.groupby('year')['netsalesamount'].sum().reset_index()
        
        col_run1, col_run2 = st.columns(2)
        
        with col_run1:
            fig_run1 = px.line(
                yearly_profit,
                x='year',
                y='netsalesamount',
                title='Динамика прибыли по годам',
                labels={'year': 'Год', 'netsalesamount': 'Прибыль'},
                markers=True
            )
            fig_run1.add_hline(y=yearly_profit['netsalesamount'].mean(), 
                             line_dash="dash",
                             annotation_text="Средняя прибыль",
                             line_color="red")
            st.plotly_chart(fig_run1, use_container_width=True)
        
        with col_run2:
            # Анализ по месяцам для последнего года
            last_year = yearly_profit['year'].max()
            monthly_data = running_suit_data[running_suit_data['year'] == last_year].copy()
            monthly_data['month'] = pd.to_datetime(monthly_data['orderdate']).dt.month
            monthly_profit = monthly_data.groupby('month')['netsalesamount'].sum().reset_index()
            
            fig_run2 = px.bar(
                monthly_profit,
                x='month',
                y='netsalesamount',
                title=f'Прибыль по месяцам ({last_year} год)',
                labels={'month': 'Месяц', 'netsalesamount': 'Прибыль'},
                color='netsalesamount'
            )
            st.plotly_chart(fig_run2, use_container_width=True)
        
        # Анализ рентабельности
        running_suit_data['profit_margin'] = (running_suit_data['netsalesamount'] / running_suit_data['grosssalesamount']) * 100
        avg_margin = running_suit_data['profit_margin'].mean()
        
        # Сравнение с другими товарами
        all_products_profit = fact_with_products.groupby('productname')['netsalesamount'].sum().reset_index()
        product_rank = (all_products_profit['netsalesamount'] > running_suit_data['netsalesamount'].sum()).mean() * 100
        
        # Вывод рекомендации
        st.subheader("Рекомендация по ассортименту")
        
        if len(yearly_profit) > 1 and yearly_profit['netsalesamount'].iloc[-1] < yearly_profit['netsalesamount'].mean():
            st.error("**Рекомендация:** Рассмотреть возможность вывода товара из ассортимента")
            st.write(f"- Прибыль за последний год ниже среднего значения ({yearly_profit['netsalesamount'].mean():,.0f} vs {yearly_profit['netsalesamount'].iloc[-1]:,.0f})")
        else:
            st.success("**Рекомендация:** Сохранить товар в ассортименте")
            st.write(f"- Прибыль за последний год выше среднего значения ({yearly_profit['netsalesamount'].mean():,.0f} vs {yearly_profit['netsalesamount'].iloc[-1]:,.0f})")
        
        st.write("**Ключевые метрики:**")
        st.write(f"- Средняя рентабельность: {avg_margin:.1f}%")
        st.write(f"- Товар прибыльнее, чем {100 - product_rank:.1f}% других товаров")
        st.write(f"- Общая прибыль за весь период: {running_suit_data['netsalesamount'].sum():,.0f}")
        
        # Анализ по странам
        if 'country' in running_suit_data.columns:
            country_profit = running_suit_data.groupby('country')['netsalesamount'].sum().reset_index()
            fig_run3 = px.pie(
                country_profit,
                names='country',
                values='netsalesamount',
                title='Распределение прибыли по странам',
                hole=0.3
            )
            st.plotly_chart(fig_run3, use_container_width=True)

except Exception as e:
    st.error(f"Произошла ошибка при анализе товара: {str(e)}")
    st.write("Проверьте наличие столбцов в данных:", list(fact_with_products.columns))

# Преобразование данных
category_plan['Date'] = pd.to_datetime(category_plan['Date'])
category_plan['Year'] = category_plan['Date'].dt.year

# Расчет ROI
category_plan['ROI'] = (category_plan['Net_Plan'] / category_plan['Gross_Plan']) * 100

# Основной заголовок
st.title('Анализ ROI по категориям и годам')

# 1. Общая динамика ROI по годам
st.header('1. Динамика ROI по годам')

# Группировка по годам
yearly_roi = category_plan.groupby('Year')['ROI'].mean().reset_index()

fig1 = px.line(
    yearly_roi,
    x='Year',
    y='ROI',
    title='Средний ROI по годам',
    markers=True
)
fig1.add_hline(
    y=yearly_roi['ROI'].mean(),
    line_dash="dash",
    annotation_text=f"Средний ROI: {yearly_roi['ROI'].mean():.1f}%",
    line_color="red"
)
st.plotly_chart(fig1)

# 2. ROI по категориям
st.header('2. Анализ ROI по категориям')

# Выбор категорий для анализа
selected_categories = st.multiselect(
    'Выберите категории:',
    options=category_plan['category_id'].unique(),
    default=category_plan['category_id'].unique()[:3]
)

# Фильтрация данных
filtered_data = category_plan[category_plan['category_id'].isin(selected_categories)]

# Группировка по году и категории
category_year_roi = filtered_data.groupby(['Year', 'category_id'])['ROI'].mean().reset_index()

# График ROI по категориям
fig2 = px.line(
    category_year_roi,
    x='Year',
    y='ROI',
    color='category_id',
    title='Динамика ROI по категориям',
    labels={'category_id': 'Категория', 'ROI': 'ROI (%)'},
    markers=True
)
st.plotly_chart(fig2)

# 3. Сравнение категорий
st.header('3. Сравнение категорий')

# Топ-5 категорий по среднему ROI
top_categories = category_plan.groupby('category_id')['ROI'].mean().nlargest(5).reset_index()

fig3 = px.bar(
    top_categories,
    x='category_id',
    y='ROI',
    color='ROI',
    title='Топ-5 категорий по ROI',
    labels={'category_id': 'Категория', 'ROI': 'Средний ROI (%)'}
)
st.plotly_chart(fig3)

# 4. Детальный анализ по годам и категориям
st.header('4. Детальный анализ')

# Выбор года для детального анализа
selected_year = st.selectbox(
    'Выберите год для детального анализа:',
    options=sorted(category_plan['Year'].unique())
)

year_data = category_plan[category_plan['Year'] == selected_year]

# График распределения ROI по категориям для выбранного года
fig4 = px.box(
    year_data,
    x='category_id',
    y='ROI',
    title=f'Распределение ROI по категориям за {selected_year} год',
    labels={'category_id': 'Категория', 'ROI': 'ROI (%)'}
)
st.plotly_chart(fig4)

# 5. Анализ эффективности инвестиций
st.header('5. Анализ эффективности инвестиций')

# Расчет общего объема инвестиций и возврата по категориям
investment_analysis = category_plan.groupby('category_id').agg(
    total_investment=('Gross_Plan', 'sum'),
    total_return=('Net_Plan', 'sum'),
    avg_roi=('ROI', 'mean')
).reset_index()

# График инвестиций vs возврата
fig5 = px.scatter(
    investment_analysis,
    x='total_investment',
    y='total_return',
    size='avg_roi',
    color='category_id',
    hover_name='category_id',
    title='Соотношение инвестиций и возврата по категориям',
    labels={
        'total_investment': 'Общий объем инвестиций',
        'total_return': 'Общий возврат',
        'avg_roi': 'Средний ROI',
        'category_id': 'Категория'
    }
)
st.plotly_chart(fig5)

# Вывод ключевых метрик
st.subheader('Ключевые метрики:')
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Средний ROI по всем данным", f"{category_plan['ROI'].mean():.1f}%")
with col2:
    st.metric("Максимальный ROI", f"{category_plan['ROI'].max():.1f}%")
with col3:
    st.metric("Минимальный ROI", f"{category_plan['ROI'].min():.1f}%")

# Таблица с данными
if st.checkbox('Показать исходные данные'):
    st.subheader('Исходные данные')
    st.dataframe(category_plan)
