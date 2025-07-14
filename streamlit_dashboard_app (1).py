import streamlit as st
import pandas as pd
import plotly.express as px

# Загрузка данных
fact_table_url = 'https://raw.githubusercontent.com/Archchfa/test_task/main/fact_table_v2.xlsx'
products_url = 'https://raw.githubusercontent.com/Archchfa/test_task/main/products_v2.xlsx'
staff_url = 'https://raw.githubusercontent.com/Archchfa/test_task/main/staff_v2.xlsx'
calendar_url = 'https://raw.githubusercontent.com/Archchfa/test_task/main/calendar_v2.xlsx'
cont_url = 'https://raw.githubusercontent.com/Archchfa/test_task/main/cont_v2.xlsx'
category_plan_url = 'План по категориям.xlsx'  # Локальный файл

# Загрузка всех данных
@st.cache_data
def load_data():
    fact_with_calendar = pd.read_excel(fact_table_url)
    products = pd.read_excel(products_url)
    staff = pd.read_excel(staff_url)
    calendar = pd.read_excel(calendar_url)
    cont = pd.read_excel(cont_url)
    category_plan = pd.read_excel(category_plan_url, sheet_name='Таблица')
    return fact_with_calendar, products, staff, calendar, cont, category_plan

fact_with_calendar, products, staff, calendar, cont, category_plan = load_data()

# Получаем соответствие category_id и categoryname из таблицы products
category_mapping = products[['categoryid', 'categoryname']].drop_duplicates()
category_mapping = category_mapping.rename(columns={'categoryid': 'category_id'})

# Объединяем с category_plan чтобы получить названия категорий
category_plan = pd.merge(category_plan, category_mapping, on='category_id', how='left')

# Подготовка данных для существующих графиков (без изменений)
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

fact_with_products = pd.merge(
    fact_with_full_info,
    products[['productid', 'productname']],
    on='productid',
    how='left'
)

# Подготовка данных для ROI анализа
category_plan['Date'] = pd.to_datetime(category_plan['Date'])
category_plan['Year'] = category_plan['Date'].dt.year
category_plan['ROI'] = (category_plan['Net_Plan'] / category_plan['Gross_Plan']) * 100

# Настройка страницы
st.set_page_config(layout="wide", page_title="Анализ продаж и ROI")

# Заголовок
st.title("📊 Комплексный анализ продаж и ROI")

# Раздел 1: Существующие графики (полностью без изменений)
st.header("1. Анализ продаж по заказчикам и странам")

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
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    fig2 = px.pie(profit_by_customer_us, names='name', values='profit_percentage',
                 title="Процент прибыли каждого магазина")
    st.plotly_chart(fig2, use_container_width=True)

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
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    top_80 = profit_by_customer_br[profit_by_customer_br['cumulative_percent'] <= 80]
    fig4 = px.bar(top_80, x='name', y='netsalesamount',
                 title="Прибыль по заказчикам (80% прибыли)")
    st.plotly_chart(fig4, use_container_width=True)

with col5:
    fig5 = px.pie(profit_by_customer_br, names='name', values='profit_percentage',
                 title="Процент прибыли")
    st.plotly_chart(fig5, use_container_width=True)

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
st.plotly_chart(fig6, use_container_width=True)

# 4. Количество заказов по странам и годам
orders_by_country_year = fact_with_full_info.groupby(['country', 'year'])['orderid'].nunique().reset_index()
fig7 = px.bar(orders_by_country_year, x='year', y='orderid', color='country',
             title="Количество заказов по странам и годам")
st.plotly_chart(fig7, use_container_width=True)

# 5. Анализ менеджеров
st.subheader("Анализ продаж менеджеров (включая 2020 год)")

manager_sales = fact_with_employeename.groupby(['employeename', 'year'])['grosssalesamount'].sum().reset_index()
fig_manager = px.bar(manager_sales, x='year', y='grosssalesamount', color='employeename',
                    barmode='group', title="Продажи по менеджерам по годам")
st.plotly_chart(fig_manager, use_container_width=True)

selected_year = st.selectbox(
    "Выберите год для анализа менеджеров:",
    sorted(fact_with_employeename['year'].unique())
)

col_pie, col_discount = st.columns(2)

with col_pie:
    year_data = fact_with_employeename[fact_with_employeename['year'] == selected_year]
    manager_percent = year_data.groupby('employeename')['grosssalesamount'].sum().reset_index()
    manager_percent['percentage'] = manager_percent['grosssalesamount'] / manager_percent['grosssalesamount'].sum() * 100
    fig_pie = px.pie(manager_percent, names='employeename', values='percentage',
                    title=f"Распределение продаж менеджеров за {selected_year} год")
    st.plotly_chart(fig_pie, use_container_width=True)

with col_discount:
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
    st.plotly_chart(fig_discount, use_container_width=True)

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
st.plotly_chart(fig_weekday, use_container_width=True)

top_day = sales_by_weekday.loc[sales_by_weekday['grosssalesamount'].idxmax()]
st.write(f"Наиболее продуктивный день недели: **{top_day['weekday_name']}** (объем продаж: {top_day['grosssalesamount']:,.0f})")

# 7. Анализ товара "Костюм для бега"
st.header("Анализ товара «Костюм для бега»")

try:
    running_suit_data = fact_with_products[fact_with_products['productname'] == 'Костюм для бега']
    
    if running_suit_data.empty:
        st.warning("Товар 'Костюм для бега' не найден в данных")
    else:
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
        
        running_suit_data['profit_margin'] = (running_suit_data['netsalesamount'] / running_suit_data['grosssalesamount']) * 100
        avg_margin = running_suit_data['profit_margin'].mean()
        
        all_products_profit = fact_with_products.groupby('productname')['netsalesamount'].sum().reset_index()
        product_rank = (all_products_profit['netsalesamount'] > running_suit_data['netsalesamount'].sum()).mean() * 100
        
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

# 8. Новый раздел: Анализ ROI из category_plan с названиями категорий из products
st.header("📈 Анализ ROI (Return on Investment)")

# Визуализация ROI
st.subheader("Динамика ROI по годам и категориям")

# Выбор категорий для отображения
selected_categories_roi = st.multiselect(
    "Выберите категории для анализа ROI:",
    options=category_plan['categoryname'].dropna().unique(),
    default=category_plan['categoryname'].dropna().unique()[:3],
    key='roi_categories'
)

# Фильтрация данных
roi_filtered = category_plan[category_plan['categoryname'].isin(selected_categories_roi)]
roi_by_year = roi_filtered.groupby(['Year', 'categoryname'])['ROI'].mean().reset_index()

# График ROI
fig_roi = px.line(
    roi_by_year,
    x='Year',
    y='ROI',
    color='categoryname',
    title='Динамика ROI по категориям',
    labels={'Year': 'Год', 'ROI': 'ROI (%)', 'categoryname': 'Категория'},
    markers=True,
    line_shape="spline"
)
fig_roi.update_layout(hovermode="x unified")
st.plotly_chart(fig_roi, use_container_width=True)

# Анализ эффективности инвестиций
st.subheader("Эффективность инвестиций по категориям")

investment_analysis = category_plan.groupby('categoryname').agg(
    total_investment=('Gross_Plan', 'sum'),
    total_return=('Net_Plan', 'sum'),
    avg_roi=('ROI', 'mean')
).reset_index().sort_values('avg_roi', ascending=False)

col_roi1, col_roi2 = st.columns(2)

with col_roi1:
    fig_invest = px.bar(
        investment_analysis,
        x='categoryname',
        y='total_investment',
        title='Общий объем инвестиций по категориям',
        labels={'categoryname': 'Категория', 'total_investment': 'Инвестиции'},
        color='avg_roi',
        color_continuous_scale='Bluered'
    )
    st.plotly_chart(fig_invest, use_container_width=True)

with col_roi2:
    fig_return = px.bar(
        investment_analysis,
        x='categoryname',
        y='total_return',
        title='Общий возврат по категориям',
        labels={'categoryname': 'Категория', 'total_return': 'Возврат'},
        color='avg_roi',
        color_continuous_scale='Bluered'
    )
    st.plotly_chart(fig_return, use_container_width=True)

# Пузырьковая диаграмма ROI
st.subheader("Соотношение инвестиций и возврата")

fig_bubble = px.scatter(
    investment_analysis,
    x='total_investment',
    y='total_return',
    size='avg_roi',
    color='categoryname',
    hover_name='categoryname',
    title='Эффективность инвестиций по категориям (размер пузырька = ROI)',
    labels={
        'total_investment': 'Общий объем инвестиций',
        'total_return': 'Общий возврат',
        'avg_roi': 'Средний ROI (%)',
        'categoryname': 'Категория'
    },
    log_x=True,
    size_max=40
)
st.plotly_chart(fig_bubble, use_container_width=True)

# Ключевые метрики ROI
st.subheader("Ключевые метрики ROI")
roi_col1, roi_col2, roi_col3 = st.columns(3)

with roi_col1:
    max_roi = category_plan['ROI'].max()
    st.metric("Максимальный ROI", f"{max_roi:.1f}%", 
              f"Категория: {category_plan.loc[category_plan['ROI'].idxmax(), 'categoryname']}")

with roi_col2:
    min_roi = category_plan['ROI'].min()
    st.metric("Минимальный ROI", f"{min_roi:.1f}%", 
              f"Категория: {category_plan.loc[category_plan['ROI'].idxmin(), 'categoryname']}")

with roi_col3:
    mean_roi = category_plan['ROI'].mean()
    st.metric("Средний ROI", f"{mean_roi:.1f}%")

# Топ категорий по ROI
st.subheader("Топ категорий по ROI")
top_categories = investment_analysis.nlargest(5, 'avg_roi')
st.dataframe(top_categories[['categoryname', 'avg_roi', 'total_investment', 'total_return']]
             .rename(columns={
                 'categoryname': 'Категория',
                 'avg_roi': 'Средний ROI (%)',
                 'total_investment': 'Общие инвестиции',
                 'total_return': 'Общий возврат'
             }).style.format({
                 'Средний ROI (%)': '{:.1f}%',
                 'Общие инвестиции': '{:,.0f}',
                 'Общий возврат': '{:,.0f}'
             }), height=250)
