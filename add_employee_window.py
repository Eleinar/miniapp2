from PySide6.QtWidgets import QDialog, QFormLayout, QLineEdit, QComboBox, QDateEdit, QDialogButtonBox
from PySide6.QtCore import Qt, QDate
from modules import create_connection, Employee, Position, Education, EmployeeEducation, EmployeePosition
from PySide6.QtCore import QDate


class AddEmployeeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить сотрудника")
        self.setGeometry(100, 100, 400, 400)

        self.layout = QFormLayout()

        # Поля для сотрудника
        self.first_name_input = QLineEdit(self)
        self.last_name_input = QLineEdit(self)
        self.surname_input = QLineEdit(self)
        self.phone_number_input = QLineEdit(self)
        self.birth_date_input = QDateEdit(self)
        self.birth_date_input.setDate(QDate.currentDate())
        self.snils_input = QLineEdit(self)
        self.inn_input = QLineEdit(self)
        self.passport_input = QLineEdit(self)
        self.work_experience_input = QLineEdit(self)
        self.hire_date_input = QDateEdit(self)
        self.hire_date_input.setDate(QDate.currentDate())

        # Добавляем поля в форму
        self.layout.addRow("Имя", self.first_name_input)
        self.layout.addRow("Фамилия", self.last_name_input)
        self.layout.addRow("Отчество", self.surname_input)
        self.layout.addRow("Телефон", self.phone_number_input)
        self.layout.addRow("Дата рождения", self.birth_date_input)
        self.layout.addRow("СНИЛС", self.snils_input)
        self.layout.addRow("ИНН", self.inn_input)
        self.layout.addRow("Паспорт", self.passport_input)
        self.layout.addRow("Стаж работы", self.work_experience_input)
        self.layout.addRow("Дата приема", self.hire_date_input)

        # Должность и отдел
        self.position_combo = QComboBox(self)
        self.department_combo = QComboBox(self)

        # Заполняем комбобоксы должностей и отделов
        session = create_connection()
        positions = session.query(Position).all()
        for position in positions:
            self.position_combo.addItem(position.name_position, position.id)  # Получаем должность

        self.department_combo.addItem('HR')
        self.department_combo.addItem('IT')
        self.department_combo.addItem('Finance')
        # Добавьте другие отделы, если необходимо

        self.layout.addRow("Должность", self.position_combo)
        self.layout.addRow("Отдел", self.department_combo)

        # Образование
        self.education_combo = QComboBox(self)
        education_list = session.query(Education).all()
        for education in education_list:
            self.education_combo.addItem(education.level_education, education.id)
        
        self.layout.addRow("Образование", self.education_combo)

        # Кнопки для добавления
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.buttons.accepted.connect(self.save_employee)
        self.buttons.rejected.connect(self.reject)

        self.layout.addWidget(self.buttons)
        self.setLayout(self.layout)

    def save_employee(self):
        session = create_connection()

        # Сохраняем сотрудника
        new_employee = Employee(
            first_name=self.first_name_input.text(),
            last_name=self.last_name_input.text(),
            surname=self.surname_input.text(),
            phone_number=self.phone_number_input.text(),
            birth_date=self.birth_date_input.date().toPython(),
            snils=self.snils_input.text(),
            inn=self.inn_input.text(),
            passport=self.passport_input.text(),
            work_experience=int(self.work_experience_input.text()),
            hire_date=self.hire_date_input.date().toPython()
        )

        session.add(new_employee)
        session.commit()

        # Сохраняем должность и отдел
        position_id = self.position_combo.currentData()
        department = self.department_combo.currentText()
        employee_position = EmployeePosition(position_id=position_id, employee_id=new_employee.id, department=department)
        session.add(employee_position)

        # Сохраняем образование
        education_id = self.education_combo.currentData()
        employee_education = EmployeeEducation(employee_id=new_employee.id, education_id=education_id)
        session.add(employee_education)

        session.commit()
        session.close()
        self.accept()