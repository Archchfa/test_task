# Подзаголовок для графика по менеджерам
st.subheader("Какой из менеджеров дает компании наибольший объем продаж?")

# Объединяем данные с таблицей staff для получения имен менеджеров
sales_by_employee_year_with_names = pd.merge(
    fact_with_full_info.groupby(['employee_id', 'year'])['grosssalesamount'].sum().reset_index(),
    staff[['employeeid', 'employeename']],
    left_on='employee_id',
    right_on='employeeid',
    how='left'
)

# Столбчатая диаграмма с группировкой (столбцы рядом)
fig_employee_sales = px.bar(
    sales_by_employee_year_with_names, 
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
    category_orders={"year": sorted(sales_by_employee_year_with_names['year'].unique())}  # Сортировка годов
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
    sorted(fact_with_employeename['year'].unique())
)

# Фильтруем данные по выбранному году
fact_with_employeename_selected_year = fact_with_employeename[
    fact_with_employeename['year'] == selected_year
]

# Агрегируем данные по сотрудникам за выбранный год
sales_by_employeename_selected_year = fact_with_employeename_selected_year.groupby(
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
