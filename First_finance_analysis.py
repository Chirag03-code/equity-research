# My first financial analysis using Python

company = "Apple"

revenue = 600
previous_revenue = 450

net_income = 110

# Calculate revenue growth
revenue_growth = (
    (revenue - previous_revenue)
    / previous_revenue
) * 100

# Calculate net profit margin
profit_margin = (net_income / revenue) * 100

print("COMPANY:", company)
print("Revenue Growth:", round(revenue_growth, 2), "%")
print("Net Profit Margin:", round(profit_margin, 2), "%")
