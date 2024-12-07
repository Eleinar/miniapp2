from PySide6.QtWidgets import QDialog, QFormLayout, QLineEdit, QComboBox, QDateEdit, QDialogButtonBox
from PySide6.QtCore import QDate
from db import create_connection, Employee
from PySide6.QtCore import QDate

class EditEmployeeDialog(QDialog):
    def __init__(self, employee_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Редактировать сотрудника")
        self.setGeometry(100, 100, 400, 350)

        self.employee_id = employee_id
        self.layout = QFormLayout()

        # Поля ввода
        self.first_name_input = QLineEdit(self)
        self.last_name_input = QLineEdit(self)
        self.surname_input = QLineEdit(self)
        self.phone_number_input = QLineEdit(self)
        self.birth_date_input = QDateEdit(self)
        self.snils_input = QLineEdit(self)
        self.inn_input = QLineEdit(self)
        self.passport_input = QLineEdit(self)
        self.work_experience_input = QLineEdit(self)
        self.hire_date_input = QDateEdit(self)
        
        self.material_status_input = QComboBox(self)
        self.material_status_input.addItem("Да")
        self.material_status_input.addItem("Нет")

        self.dismissal_date_input = QDateEdit(self)

        # Загружаем данные сотрудника из базы данных
        session = create_connection()
        employee = session.query(Employee).filter(Employee.id == self.employee_id).first()

        self.last_name_input.setText(employee.last_name)
        self.first_name_input.setText(employee.first_name)
        self.surname_input.setText(employee.surname)
        self.phone_number_input.setText(employee.phone_number)
        self.birth_date_input.setDate(QDate(employee.birth_date.year, employee.birth_date.month, employee.birth_date.day))
        self.snils_input.setText(employee.snils)
        self.inn_input.setText(employee.inn)
        self.passport_input.setText(employee.passport)
        self.work_experience_input.setText(str(employee.work_experience))
        self.hire_date_input.setDate(QDate(employee.hire_date.year, employee.hire_date.month, employee.hire_date.day))

        self.material_status_input.setCurrentIndex(0 if employee.material_status else 1)
        if employee.dismissal_date:
            self.dismissal_date_input.setDate(QDate(employee.dismissal_date.year, employee.dismissal_date.month, employee.dismissal_date.day))
        else:
            self.dismissal_date_input.setDate(QDate.currentDate())

        # Добавление элементов
        self.layout.addRow("Фамилия", self.last_name_input)
        self.layout.addRow("Имя", self.first_name_input)
        self.layout.addRow("Отчество", self.surname_input)
        self.layout.addRow("Телефон", self.phone_number_input)
        self.layout.addRow("Дата рождения", self.birth_date_input)
        self.layout.addRow("СНИЛС", self.snils_input)
        self.layout.addRow("ИНН", self.inn_input)
        self.layout.addRow("Паспорт", self.passport_input)
        self.layout.addRow("Стаж работы", self.work_experience_input)
        self.layout.addRow("Дата приема", self.hire_date_input)
        self.layout.addRow("Материальный статус", self.material_status_input)
        self.layout.addRow("Дата увольнения", self.dismissal_date_input)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.buttons.accepted.connect(self.save_changes)
        self.buttons.rejected.connect(self.reject)

        self.layout.addWidget(self.buttons)
        self.setLayout(self.layout)

    def save_changes(self):
        session = create_connection()
        employee = session.query(Employee).filter(Employee.id == self.employee_id).first()

        # Обновляем данные
        employee.first_name = self.first_name_input.text()
        employee.last_name = self.last_name_input.text()
        employee.surname = self.surname_input.text()
        employee.phone_number = self.phone_number_input.text()
        employee.birth_date = self.birth_date_input.date().toPython()  # Используем toPython()
        employee.snils = self.snils_input.text()
        employee.inn = self.inn_input.text()
        employee.passport = self.passport_input.text()
        employee.work_experience = int(self.work_experience_input.text())
        employee.hire_date = self.hire_date_input.date().toPython()  # Используем toPython()

        session.commit()
        session.close()
        self.accept()