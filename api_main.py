import json
import requests
from typing import Optional, Dict, Any, Union
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QPushButton, QTableWidget, QTableWidgetItem, QLabel)
from PyQt5.QtCore import Qt
import sys

class ApiConfigLoader:
    _CONFIG_PATH = "Api.json"
    
    @classmethod
    def get_api_key(cls) -> str:
        try:
            with open(cls._CONFIG_PATH) as config_file:
                config_data = json.load(config_file)
                return config_data.get('api_key', '')
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Конфигурационная ошибка: {str(e)}")
            return ''

class ApiClient:
    BASE_DOMAIN = "https://api.ataix.kz"
    
    def __init__(self):
        self.auth_header = {
            "API-KEY": ApiConfigLoader.get_api_key(),
            "Accept": "application/json"
        }
    
    def _send_request(self, path: str) -> Union[Dict[str, Any], str]:
        full_url = f"{self.BASE_DOMAIN}{path}"
        try:
            response = requests.get(
                full_url,
                headers=self.auth_header,
                timeout=15
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            return "Таймаут соединения"
        except requests.exceptions.HTTPError as http_err:
            return f"HTTP ошибка: {http_err}"
        except Exception as general_err:
            return f"Ошибка: {general_err}"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.client = ApiClient()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Криптотрейдинговая платформа")
        self.setGeometry(100, 100, 800, 600)

        # Создаем центральный виджет и layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Заголовок
        title = QLabel("КРИПТОТРЕЙДИНГОВАЯ ПЛАТФОРМА")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Кнопки
        btn_currencies = QPushButton("Список криптовалют")
        btn_symbols = QPushButton("Торговые пары")
        btn_prices = QPushButton("Актуальные цены")
        btn_exit = QPushButton("Выход")

        # Подключение кнопок к обработчикам
        btn_currencies.clicked.connect(lambda: self.display_data('/api/currencies'))
        btn_symbols.clicked.connect(lambda: self.display_data('/api/symbols'))
        btn_prices.clicked.connect(lambda: self.display_data('/api/prices'))
        btn_exit.clicked.connect(self.close)

        # Добавление кнопок в layout
        layout.addWidget(btn_currencies)
        layout.addWidget(btn_symbols)
        layout.addWidget(btn_prices)
        layout.addWidget(btn_exit)

        # Таблица для отображения данных
        self.table = QTableWidget()
        layout.addWidget(self.table)

    def display_data(self, endpoint: str):
        # Получаем данные
        data = self.client._send_request(endpoint)
        
        if isinstance(data, str):  # Если вернулась ошибка
            self.table.setRowCount(1)
            self.table.setColumnCount(1)
            self.table.setItem(0, 0, QTableWidgetItem(data))
            return

        # Извлекаем данные из поля 'result', если оно есть
        if isinstance(data, dict) and 'result' in data:
            data = data['result']

        # Если данные - список словарей
        if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
            # Устанавливаем размеры таблицы
            self.table.setRowCount(len(data))
            columns = list(data[0].keys())
            self.table.setColumnCount(len(columns))
            self.table.setHorizontalHeaderLabels(columns)

            # Заполняем таблицу
            for row_idx, row_data in enumerate(data):
                for col_idx, value in enumerate(row_data.values()):
                    self.table.setItem(row_idx, col_idx, 
                                     QTableWidgetItem(str(value)))
                    
            self.table.resizeColumnsToContents()
        else:
            # Для простых данных
            self.table.setRowCount(1)
            self.table.setColumnCount(1)
            self.table.setItem(0, 0, QTableWidgetItem(json.dumps(data, indent=2)))

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()