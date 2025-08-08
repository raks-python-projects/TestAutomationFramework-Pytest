import os
import csv
import matplotlib.pyplot as plt


class TestAvailabilityStock:
    def test_discontinued_stock(self, request):
        input_file = os.environ.get('USER_INPUT_FILE')
        assert input_file and input_file.endswith('.csv')
        names = []
        stocks = []
        colors = []
        failed = False
        fail_msgs = []
        import pandas as pd
        df = pd.read_csv(input_file, delimiter=',', encoding='utf-8')
        for _, row in df.iterrows():
            name = row['Name']
            stock = int(row['Stock'])
            availability = row['Availability']
            names.append(name)
            stocks.append(stock)
            if availability == 'discontinued':
                colors.append('red')
                if stock == 0:
                    failed = True
                    fail_msgs.append(f"FAIL: {name} is discontinued but stock is {stock}")
            else:
                colors.append('green')
        # Plot
        plt.figure(figsize=(10, 6))
        plt.bar(names, stocks, color=colors)
        plt.xticks(rotation=45, ha='right')
        plt.xlabel('Product Name')
        plt.ylabel('Stock')
        plt.title('Stock by Product (Red=Discontinued)')
        plt.tight_layout()
        plot_path = 'stock_plot.png'
        plt.savefig(plot_path)
        plt.close()
        # Attach plot to pytest-html report
        if request.config.pluginmanager.hasplugin("html"):
            import pytest_html
            with open(plot_path, "rb") as image_file:
                image_data = image_file.read()
            extra = getattr(pytest_html, 'extras', None)
            if extra:
                request.node.extra = getattr(request.node, 'extra', [])
                request.node.extra.append(extra.image(image_data, mime_type='image/png', extension='png'))
        # Assert
        assert not failed, "\n".join(fail_msgs)

# Optional: pytest-html hook to add extras
def pytest_html_results_table_row(report, cells):
    if hasattr(report, 'extra'):
        for extra in report.extra:
            if extra['content_type'].startswith('image'):
                cells.append(f'<img src="data:{extra["content_type"]};base64,{extra["content"]}" width="400"/>')