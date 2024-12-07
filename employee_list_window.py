from PySide6.QtWidgets import QMessageBox, QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHBoxLayout, QDialog

from db import create_connection, Employee, EmployeeEducation, EmployeePosition, EmployeeTraining
from edit_employee_window import EditEmployeeDialog
from add_employee_window import AddEmployeeDialog
from fpdf import FPDF


class EmployeeListWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Список сотрудников")
        self.setGeometry(100, 100, 1300, 600)

        self.layout = QVBoxLayout()

        # Таблица сотрудников
        self.table = QTableWidget(self)
        self.layout.addWidget(self.table)

        # Кнопки действий
        self.buttons_panel = QHBoxLayout()
        self.add_button = QPushButton("Добавить сотрудника", self)
        self.add_button.clicked.connect(self.add_employee)
        self.buttons_panel.addWidget(self.add_button)

        self.update_button = QPushButton("Редактировать", self)
        self.update_button.clicked.connect(self.update_employee)
        self.buttons_panel.addWidget(self.update_button)

        self.delete_button = QPushButton("Удалить", self)
        self.delete_button.clicked.connect(self.delete_employee)
        self.buttons_panel.addWidget(self.delete_button)

        self.report_button = QPushButton("Генерировать отчет", self)
        self.report_button.clicked.connect(self.generate_training_report)
        self.buttons_panel.addWidget(self.report_button)

        self.layout.addLayout(self.buttons_panel)

        self.setLayout(self.layout)

        # Загружаем данные сотрудников
        self.load_employees()
        
    def load_employees(self):
        """Загружаем список сотрудников из базы данных"""
        session = create_connection()
        employees = session.query(Employee).filter(Employee.is_deleted == False).all()  # Фильтруем по удаленным
        self.table.setRowCount(len(employees))
        self.table.setColumnCount(13)  # Добавим столбец для id

        # Устанавливаем заголовки столбцов
        self.table.setHorizontalHeaderLabels([
            "", "Фамилия", "Имя", "Отчество", "Телефон", "Дата рождения", 
            "СНИЛС", "ИНН", "Паспорт", "Стаж работы", "Семейное положение", 
            "Дата приема", "Дата увольнения"
        ])

        for row, employee in enumerate(employees):
            # Устанавливаем видимые данные
            self.table.setItem(row, 0, QTableWidgetItem(str(employee.id)))  # Добавляем id в скрытый столбец
            self.table.setItem(row, 1, QTableWidgetItem(employee.last_name))  # Фамилия
            self.table.setItem(row, 2, QTableWidgetItem(employee.first_name))  # Имя
            self.table.setItem(row, 3, QTableWidgetItem(employee.surname))  # Отчество
            self.table.setItem(row, 4, QTableWidgetItem(employee.phone_number))  # Телефон
            self.table.setItem(row, 5, QTableWidgetItem(str(employee.birth_date)))  # Дата рождения
            self.table.setItem(row, 6, QTableWidgetItem(employee.snils))  # СНИЛС
            self.table.setItem(row, 7, QTableWidgetItem(employee.inn))  # ИНН
            self.table.setItem(row, 8, QTableWidgetItem(employee.passport))  # Паспорт
            self.table.setItem(row, 9, QTableWidgetItem(str(employee.work_experience)))  # Стаж работы
            self.table.setItem(row, 10, QTableWidgetItem("Да" if employee.material_status else "Нет"))  # Материальный статус
            self.table.setItem(row, 11, QTableWidgetItem(str(employee.hire_date)))  # Дата приема
            self.table.setItem(row, 12, QTableWidgetItem(str(employee.dismissal_date) if employee.dismissal_date else 'Нет'))  # Дата увольнения

        # Автоматическая настройка ширины столбцов
        self.table.resizeColumnsToContents()

        # Скрываем первый столбец (с id)
        self.table.setColumnHidden(0, True)

        # Настроим горизонтальную прокрутку для длинных строк
        self.table.horizontalHeader().setStretchLastSection(True)

        session.close()

    def delete_employee(self):
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            employee_id = int(self.table.item(selected_row, 0).text())  # Приводим к int
            session = create_connection()
            employee = session.query(Employee).filter(Employee.id == employee_id).first()
            if employee:
                employee.is_deleted = True
                session.commit()
            session.close()
            self.load_employees()

    def restore_employee(self):
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            employee_id = int(self.table.item(selected_row, 0).text())  # Приводим к int
            session = create_connection()
            employee = session.query(Employee).filter(Employee.id == employee_id).first()
            if employee:
                employee.is_deleted = False
                session.commit()
            session.close()
            self.load_employees()

    def update_employee(self):
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            # Получаем ID сотрудника из скрытого столбца (столбец 0)
            employee_id = self.table.item(selected_row, 0).text()
            if employee_id.isdigit():  # Проверяем, что это число
                employee_id = int(employee_id)
                dialog = EditEmployeeDialog(employee_id, self)
                if dialog.exec() == QDialog.Accepted:
                    self.load_employees()
            else:
                self.show_message("Ошибка", "Некорректный ID сотрудника.", QMessageBox.Critical)

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

    def add_employee(self):
        dialog = AddEmployeeDialog(self)
        if dialog.exec() == QDialog.Accepted:
            self.load_employees()  # Обновляем таблицу после добавления сотрудника

    
    def show_message(self, title, message, icon=QMessageBox.Information):
        """Отображает всплывающее сообщение."""
        msg_box = QMessageBox(self)
        msg_box.setIcon(icon)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec()

    def generate_training_report(self):
        try:
            session = create_connection()

            # Загружаем список сотрудников, прошедших обучение в определенный период
            employees = session.query(Employee).filter(Employee.is_deleted == False).all()

            # Создаем объект PDF
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()

            # Заголовок
            pdf.set_font('FreeSans', '', 16)
            pdf.cell(200, 10, "Отчет об обучении сотрудников", ln=True, align='C')
            pdf.ln(10)

            total_amount = 0  # Общая сумма

            # Заголовки столбцов
            pdf.set_font('FreeSans', '', 12)
            pdf.cell(60, 10, "ФИО", border=1)
            pdf.cell(60, 10, "Название курса", border=1)
            pdf.cell(30, 10, "Дата окончания", border=1)
            pdf.cell(30, 10, "Стоимость", border=1)
            pdf.ln()

            # Данные по каждому сотруднику
            pdf.set_font('FreeSans', '', 12)
            for employee in employees:
                # Получаем курсы и обучение для каждого сотрудника
                training = session.query(EmployeeTraining).filter(EmployeeTraining.employee_id == employee.id).all()

                for t in training:
                    pdf.cell(60, 10, f"{employee.last_name} {employee.first_name}", border=1)
                    pdf.cell(60, 10, t.r_training.name_training, border=1)
                    pdf.cell(30, 10, str(t.end_date), border=1)  # Предполагаем, что у EmployeeTraining есть end_date
                    pdf.cell(30, 10, f"{t.price:.2f} р.", border=1)
                    pdf.ln()
                    total_amount += t.price

            # Итоговая сумма
            pdf.ln(10)
            pdf.set_font('FreeSans', '', 14)
            pdf.cell(0, 10, f"Итого за обучение: {total_amount:.2f} р.", ln=True, align='R')

            # Сохраняем PDF
            pdf_output_path = f"./training_report.pdf"
            pdf.output(pdf_output_path)

            print(f"Отчет был успешно экспортирован в {pdf_output_path}")
            session.close()

        except Exception as e:
            print(f"Произошла ошибка при создании отчета: {str(e)}")
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка при создании отчета: {str(e)}")

    def generate_employee_card_report(self):
        try:
            session = create_connection()

            # Загружаем сотрудников
            employees = session.query(Employee).filter(Employee.is_deleted == False).all()

            for employee in employees:
                # Создаем объект PDF для каждого сотрудника
                pdf = FPDF()
                pdf.set_auto_page_break(auto=True, margin=15)
                pdf.add_page()

                # Заголовок
                pdf.set_font('FreeSans', '', 16)
                pdf.cell(200, 10, f"Карточка сотрудника: {employee.last_name} {employee.first_name}", ln=True, align='C')
                pdf.ln(10)

                # Информация о сотруднике
                pdf.set_font('FreeSans', '', 12)
                pdf.cell(200, 10, f"ФИО: {employee.last_name} {employee.first_name}", ln=True)

                # Должность
                position = session.query(EmployeePosition).filter(EmployeePosition.employee_id == employee.id).first()
                if position:
                    pdf.cell(200, 10, f"Должность: {position.r_position.name_position}", ln=True)
                    pdf.cell(200, 10, f"Отдел: {position.department}", ln=True)

                # Образование
                education = session.query(EmployeeEducation).filter(EmployeeEducation.employee_id == employee.id).first()
                if education:
                    pdf.cell(200, 10, f"Образование: {education.r_education.level_education}", ln=True)
                else:
                    pdf.cell(200, 10, "Образование: Не указано", ln=True)

                # Курсы обучения
                training_list = session.query(EmployeeTraining).filter(EmployeeTraining.employee_id == employee.id).all()
                pdf.cell(200, 10, "Пройденные курсы:", ln=True)

                if training_list:
                    for t in training_list:
                        pdf.cell(200, 10, f"{t.r_training.name_training} - {str(t.end_date)}", ln=True)
                else:
                    pdf.cell(200, 10, "Нет пройденных курсов", ln=True)

                # Сохраняем PDF для каждого сотрудника
                pdf_output_path = f"./employee_card_{employee.id}.pdf"
                pdf.output(pdf_output_path)

                print(f"Карточка сотрудника была успешно экспортирована в {pdf_output_path}.")

            session.close()

        except Exception as e:
            print(f"Произошла ошибка при создании карточки сотрудника: {str(e)}")
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка при создании карточки сотрудника: {str(e)}")