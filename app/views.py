from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Sale, InventoryLog
from django.contrib import messages
from django.shortcuts import render
from .models import Sale, Product
from django.db.models import Sum, Count
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from sklearn.linear_model import LinearRegression
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def product_list(request):
    products = Product.objects.all()
    return render(request, 'store/product_list.html', {'products': products})

def sell_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        quantity = int(request.POST['quantity'])
        if quantity > product.quantity_in_stock:
            messages.error(request, "Not enough stock available.")
            return redirect('sell_product', product_id=product.id)

        sale = Sale(product=product, quantity=quantity)
        sale.save()
        product.quantity_in_stock -= quantity
        product.save()

        InventoryLog.objects.create(product=product, change_in_quantity=-quantity)
        messages.success(request, f'Sold {quantity} units of {product.name}.')

        return redirect('product_list')
    
    return render(request, 'store/sell_product.html', {'product': product})



def profit_loss_report(request):
    # Fetch all sales data
    sales = Sale.objects.all()

    # Prepare the data for machine learning
    sales_data = []
    for sale in sales:
        sales_data.append({
            'product_name': sale.product.name,
            'purchase_price': float(sale.product.purchase_price),
            'selling_price': float(sale.product.selling_price),
            'quantity': sale.quantity,
            'profit': float(sale.profit),
            'sale_date': sale.sale_date,
        })

    # Convert to DataFrame for easier manipulation
    sales_df = pd.DataFrame(sales_data)

    # Extract features and target variable
    X = sales_df[['purchase_price', 'selling_price', 'quantity']]  # Features: purchase price, selling price, and quantity
    y = sales_df['profit']  # Target: profit

    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Create and train the Linear Regression model
    model = LinearRegression()
    model.fit(X_train, y_train)

    # Make predictions on the test set
    y_pred = model.predict(X_test)

    # Calculate evaluation metrics
    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    adj_r2 = 1 - (1 - r2) * (len(y_test) - 1) / (len(y_test) - X_test.shape[1] - 1)

    # Calculate total profit
    total_profit = sum(sale.profit for sale in sales)

    context = {
        'sales': sales,
        'total_profit': total_profit,
        'mae': mae,
        'mse': mse,
        'r2': r2,
        'adj_r2': adj_r2
    }

    return render(request, 'store/profit_loss_report.html', context)


def analytics(request):
    # Descriptive Analytics
    sales = Sale.objects.select_related('product').all()
    
    total_sales = sum(sale.total_price for sale in sales)
    total_products_sold = sum(sale.quantity for sale in sales)
    average_sale_value = total_sales / total_products_sold if total_products_sold > 0 else 0
    
    max_sale = max(sales, key=lambda s: s.total_price, default=None)
    min_sale = min(sales, key=lambda s: s.total_price, default=None)
    
    product_count = Product.objects.count()
    
    product_sales = Sale.objects.values('product__name').annotate(total_quantity=Sum('quantity'))
    most_sold_product = max(product_sales, key=lambda p: p['total_quantity'], default=None)
    
    sales_data = []
    for sale in sales:
        sales_data.append({
            'product_name': sale.product.name,
            'quantity': sale.quantity,
            'profit': float(sale.profit),
            'sale_date': sale.sale_date
        })
    
    sales_df = pd.DataFrame(sales_data)
    
    X = sales_df[['quantity']].values.reshape(-1, 1)
    y = sales_df['profit'].values
    
    model = LinearRegression()
    model.fit(X, y)
    predictions = model.predict(X)
    
    # Create Plotly graphs
    def create_bar_graph(x, y, title, xaxis_title, yaxis_title):
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=x,
            y=y,
            text=[f'${v:,.2f}' for v in y],
            textposition='auto',
            marker_color='blue'
        ))
        fig.update_layout(
            title=title,
            xaxis_title=xaxis_title,
            yaxis_title=yaxis_title,
            plot_bgcolor='rgba(0, 0, 0, 0)',
            paper_bgcolor='rgba(0, 0, 0, 0)',
            xaxis=dict(showgrid=True, gridcolor='#cecdcd'),
            yaxis=dict(showgrid=True, gridcolor='#cecdcd'),
            font=dict(
                family='Roboto, sans-serif',
                size=16,
                color='#315c74'
            ),
            showlegend=True
        )
        return pio.to_html(fig, full_html=False)

    def create_scatter_plot(x, y, line_x, line_y, title, xaxis_title, yaxis_title):
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=x,
            y=y,
            mode='markers',
            name='Actual Profit',
            marker=dict(color='blue')
        ))
        fig.add_trace(go.Scatter(
            x=line_x,
            y=line_y,
            mode='lines',
            name='Regression Line',
            line=dict(color='red')
        ))
        fig.update_layout(
            title=title,
            xaxis_title=xaxis_title,
            yaxis_title=yaxis_title,
            plot_bgcolor='rgba(0, 0, 0, 0)',
            paper_bgcolor='rgba(0, 0, 0, 0)',
            xaxis=dict(showgrid=True, gridcolor='#cecdcd'),
            yaxis=dict(showgrid=True, gridcolor='#cecdcd'),
            font=dict(
                family='Roboto, sans-serif',
                size=16,
                color='#315c74'
            ),
            showlegend=True
        )
        return pio.to_html(fig, full_html=False)

    # Bar graph for total profit by product
    profit_graph = create_bar_graph(
        sales_df['product_name'].unique(),
        sales_df.groupby('product_name')['profit'].sum(),
        'Total Profit by Product',
        'Product',
        'Total Profit ($)'
    )
    
    # Scatter plot with regression line
    regression_plot = create_scatter_plot(
        sales_df['quantity'],
        y,
        sales_df['quantity'],
        predictions,
        'Profit Regression Analysis',
        'Quantity Sold',
        'Profit ($)'
    )

    # Sales data details
    sales_df['predicted_profit'] = predictions
    sales_df['residual'] = sales_df['profit'] - sales_df['predicted_profit']
    
    sales_data_details = sales_df[['product_name', 'quantity', 'profit', 'predicted_profit', 'residual']]
    sales_data_list = sales_data_details.to_dict(orient='records')
    
    # Calculate sums
    sum_actual_y = sales_df['profit'].sum()
    sum_predicted_y = sales_df['predicted_profit'].sum()
    sum_residual = sales_df['residual'].sum()

    # Metrics for Regression
    correlation = np.corrcoef(X.flatten(), y)[0, 1]
    r2 = model.score(X, y)
    adj_r2 = 1 - (1 - r2) * (len(y) - 1) / (len(y) - X.shape[1] - 1)

    context = {
        'total_sales': total_sales,
        'total_products_sold': total_products_sold,
        'average_sale_value': average_sale_value,
        'max_sale': max_sale,
        'min_sale': min_sale,
        'product_count': product_count,
        'most_sold_product': most_sold_product,
        'profit_graph': profit_graph,
        'regression_plot': regression_plot,
        'correlation': correlation,
        'r2': r2,
        'adj_r2': adj_r2,
        'sales_data': sales_data_list,
        'sum_actual_y': sum_actual_y,
        'sum_predicted_y': sum_predicted_y,
        'sum_residual': sum_residual
    }
    return render(request, 'store/analytics.html', context)
