from PySide6.QtWidgets import QApplication
from employee_list_window import EmployeeListWindow

app = QApplication([])
window = EmployeeListWindow()
window.show()
app.exec()
