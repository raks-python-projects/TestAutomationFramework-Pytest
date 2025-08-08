import sys
import os
import importlib.util
import glob
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QMessageBox, QProgressBar
)
from PyQt5.QtWidgets import QTableWidgetItem, QComboBox as QComboBoxWidget
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import subprocess


class TestRunnerThread(QThread):
    finished = pyqtSignal(str)

    def __init__(self, test_class, input_file):
        super().__init__()
        self.test_class = test_class
        self.input_file = input_file

    def run(self):
        report_path = os.path.join('reports', 'report.html')
        os.makedirs('reports', exist_ok=True)
        # Pass input_file as an environment variable
        env = os.environ.copy()
        env['USER_INPUT_FILE'] = self.input_file
        subprocess.run([
            sys.executable, '-m', 'pytest', self.test_class,
            '--html', report_path, '--self-contained-html'
        ], env=env)
        self.finished.emit(report_path)

class TestApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Test Runner')
        self.setGeometry(100, 100, 800, 600)
        self.input_file = None
        self.test_classes = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Top bar layout
        from PyQt5.QtWidgets import QHBoxLayout, QLineEdit, QComboBox, QLabel
        top_bar = QHBoxLayout()

        # Load button (top left)
        self.load_btn = QPushButton('📂')
        self.load_btn.setFixedSize(40, 40)
        self.load_btn.setStyleSheet("""
            QPushButton {
                background-color: #1976d2;
                color: white;
                font-size: 18px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
        """)
        self.load_btn.clicked.connect(self.load_file)
        load_layout = QVBoxLayout()
        load_label = QLabel('Load File')
        load_label.setAlignment(Qt.AlignCenter)
        load_layout.addWidget(self.load_btn, alignment=Qt.AlignLeft)
        load_layout.addWidget(load_label)
        top_bar.addLayout(load_layout)
        top_bar.addSpacing(20)

        # Project info fields (center, more space)
        self.project_name = QLineEdit()
        self.project_name.setPlaceholderText('Project Name')
        self.project_name.setFixedWidth(220)
        self.project_name.setStyleSheet("background: #fff; border: 1px solid #1976d2; border-radius: 6px;")
        project_layout = QVBoxLayout()
        project_label = QLabel('Project Name')
        project_label.setAlignment(Qt.AlignCenter)
        project_layout.addWidget(self.project_name)
        project_layout.addWidget(project_label)
        top_bar.addLayout(project_layout)
        top_bar.addSpacing(20)

        self.test_type = QComboBox()
        self.test_type.addItems(['Functional', 'Regression', 'Smoke', 'Custom'])
        self.test_type.setFixedWidth(180)
        self.test_type.setStyleSheet("background: #fff; border: 1px solid #1976d2; border-radius: 6px;")
        type_layout = QVBoxLayout()
        type_label = QLabel('Test Type')
        type_label.setAlignment(Qt.AlignCenter)
        type_layout.addWidget(self.test_type)
        type_layout.addWidget(type_label)
        top_bar.addLayout(type_layout)
        top_bar.addSpacing(20)

        self.sw_version = QLineEdit()
        self.sw_version.setPlaceholderText('SW Release Version')
        self.sw_version.setFixedWidth(220)
        self.sw_version.setStyleSheet("background: #fff; border: 1px solid #1976d2; border-radius: 6px;")
        sw_layout = QVBoxLayout()
        sw_label = QLabel('SW Version')
        sw_label.setAlignment(Qt.AlignCenter)
        sw_layout.addWidget(self.sw_version)
        sw_layout.addWidget(sw_label)
        top_bar.addLayout(sw_layout)
        top_bar.addStretch(1)

        # Refresh button
        self.refresh_btn = QPushButton('🔄')
        self.refresh_btn.setFixedSize(40, 40)
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #388e3c;
                color: white;
                font-size: 18px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2e7d32;
            }
        """)
        self.refresh_btn.clicked.connect(self.load_test_classes)
        refresh_layout = QVBoxLayout()
        refresh_label = QLabel('Refresh')
        refresh_label.setAlignment(Qt.AlignCenter)
        refresh_layout.addWidget(self.refresh_btn)
        refresh_layout.addWidget(refresh_label)
        top_bar.addLayout(refresh_layout)
        top_bar.addSpacing(10)

        # Run button
        self.run_btn = QPushButton('▶️')
        self.run_btn.setFixedSize(40, 40)
        self.run_btn.setStyleSheet("""
            QPushButton {
                background-color: #fbc02d;
                color: #222;
                font-size: 18px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f9a825;
            }
        """)
        self.run_btn.clicked.connect(self.run_test)
        run_layout = QVBoxLayout()
        run_label = QLabel('Run')
        run_label.setAlignment(Qt.AlignCenter)
        run_layout.addWidget(self.run_btn)
        run_layout.addWidget(run_label)
        top_bar.addLayout(run_layout)

        layout.addLayout(top_bar)

        # Middle area: list of loaded files and test selection
        from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QAbstractItemView, QHeaderView, \
            QComboBox as QComboBoxWidget

        self.file_table = QTableWidget(0, 2)
        self.file_table.setHorizontalHeaderLabels(['Loaded File', 'Select Test Case'])
        self.file_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.file_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.file_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.file_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.file_table.setStyleSheet("""
            QTableWidget {
                background: #f5f5f5;
                border: 2px solid #1976d2;
                font-size: 15px;
                border-radius: 8px;
            }
            QTableWidget::item:selected {
                background: #bbdefb;
                color: #222;
            }
        """)
        layout.addWidget(self.file_table)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setVisible(False)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #1976d2;
                border-radius: 8px;
                text-align: center;
                height: 22px;
                background: #e3f2fd;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #43cea2, stop:1 #1976d2);
                width: 30px;
            }
        """)
        layout.addWidget(self.progress)

        self.setLayout(layout)
        self.setStyleSheet("""
            QWidget {
                background: #e3f2fd;
            }
        """)
        self.test_classes = []
        self.loaded_files = []
        self.load_test_classes()

    def load_file(self):
        file, _ = QFileDialog.getOpenFileName(self, 'Open File', '', 'CSV/Excel Files (*.csv *.xlsx *.xls)')
        if file:
            if file not in self.loaded_files:
                self.loaded_files.append(file)
                row = self.file_table.rowCount()
                self.file_table.insertRow(row)
                self.file_table.setItem(row, 0, QTableWidgetItem(os.path.basename(file)))
                # Test case selection per file
                combo = QComboBoxWidget()
                combo.addItems([tc for tc in self.test_classes])
                self.file_table.setCellWidget(row, 1, combo)

    def load_test_classes(self):
        self.test_classes = []
        for file in glob.glob('tests/*.py'):
            module_name = os.path.splitext(os.path.basename(file))[0]
            spec = importlib.util.spec_from_file_location(module_name, file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            for attr in dir(module):
                obj = getattr(module, attr)
                if isinstance(obj, type) and attr.startswith('Test'):
                    self.test_classes.append(f'tests/{module_name}.py::{attr}')
        # Update test case combos in file table
        for row in range(self.file_table.rowCount()):
            combo = self.file_table.cellWidget(row, 1)
            if combo:
                combo.clear()
                combo.addItems([tc for tc in self.test_classes])

    def run_test(self):
        if self.file_table.rowCount() == 0:
            QMessageBox.warning(self, 'Error', 'Load at least one file.')
            return
        # Collect selected test cases for each file
        self.file_test_pairs = []
        for row in range(self.file_table.rowCount()):
            file_item = self.loaded_files[row]
            combo = self.file_table.cellWidget(row, 1)
            if combo and combo.currentText():
                self.file_test_pairs.append((file_item, combo.currentText()))
        if not self.file_test_pairs:
            QMessageBox.warning(self, 'Error', 'Select at least one test case for a loaded file.')
            return
        self.progress.setVisible(True)
        self.reports = []
        self.completed = 0
        self.total = len(self.file_test_pairs)
        self.run_next_test()

    def run_next_test(self):
        if self.completed < self.total:
            input_file, test_class = self.file_test_pairs[self.completed]
            self.runner = TestRunnerThread(test_class, input_file)
            self.runner.finished.connect(self.collect_report)
            self.runner.start()
        else:
            self.show_summary_page()

    def collect_report(self, report_path):
        self.reports.append(report_path)
        self.completed += 1
        self.run_next_test()

    def show_summary_page(self):
        self.progress.setVisible(False)
        from PyQt5.QtWidgets import QTabWidget, QTextBrowser, QDialog, QVBoxLayout
        dialog = QDialog(self)
        dialog.setWindowTitle('Test Results')
        dialog.resize(800, 600)
        layout = QVBoxLayout(dialog)
        tabs = QTabWidget()
        # Front page: summary of testcases
        summary = QTextBrowser()
        summary.setHtml(
            f'<h2>Test Case Summary</h2>'
            f'<b>Project Name:</b> {self.project_name.text()}<br>'
            f'<b>Test Type:</b> {self.test_type.currentText()}<br>'
            f'<b>SW Release Version:</b> {self.sw_version.text()}<br>'
            '<ul>' +
            ''.join(f'<li>{os.path.basename(pair[0])} - {pair[1]}</li>' for pair in self.file_test_pairs) +
            '</ul>'
        )
        tabs.addTab(summary, 'Summary')
        # Add a tab for each report (plots, tables, failed info)
        for report_path in self.reports:
            browser = QTextBrowser()
            with open(report_path, 'r', encoding='utf-8') as f:
                html = f.read()
            browser.setHtml(html)
            tabs.addTab(browser, os.path.basename(report_path))
        layout.addWidget(tabs)
        dialog.setLayout(layout)
        dialog.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TestApp()
    window.show()
    sys.exit(app.exec_())