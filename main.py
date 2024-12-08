from employee_list_window import EmployeeListWindow
from PySide6.QtWidgets import QApplication

app = QApplication() 
window = EmployeeListWindow()
window.show()
app.exec()
