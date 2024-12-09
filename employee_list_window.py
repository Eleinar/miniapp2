from PySide6.QtWidgets import QMessageBox, QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHBoxLayout, QDialog
from modules import create_connection, Employee, EmployeeEducation, EmployeePosition, Training, EmployeeTraining
from fpdf import FPDF

from add_training_window import AddTrainingDialog
from add_employee_window import AddEmployeeDialog
from edit_employee_window import EditEmployeeDialog

class EmployeeListWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Список сотрудников")
        self.setGeometry(100, 100, 1300, 600)

        self.layout = QVBoxLayout()

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

        self.report_button1 = QPushButton("Документ 1", self)
        self.report_button1.clicked.connect(self.generate_training_report)
        self.buttons_panel.addWidget(self.report_button1)
        
        self.report_button2 = QPushButton("Документ 2", self)
        self.report_button2.clicked.connect(self.generate_employee_card_report)
        self.buttons_panel.addWidget(self.report_button2)
        
        self.layout.addLayout(self.buttons_panel)

         # Таблица сотрудников
        self.table = QTableWidget(self)
        self.layout.addWidget(self.table)

        self.setLayout(self.layout)

        # Загружаем данные сотрудников
        self.load_employees()
        
    def load_employees(self):
        # Загружаем список сотрудников из базы данных
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
        # Отображает всплывающее сообщение.
        msg_box = QMessageBox(self)
        msg_box.setIcon(icon)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec()

    def generate_training_report(self):
        try:
            session = create_connection()

            # Извлечение данных о сотрудниках и их обучении
            data = (
                session.query(
                    Employee.last_name,
                    Employee.first_name,
                    Employee.surname,
                    Training.start_date,
                    Training.end_date,
                    Training.name_training,
                    Training.format_training
                )
                .join(EmployeeTraining, Employee.id == EmployeeTraining.employee_id)
                .join(Training, EmployeeTraining.training_id == Training.id)
                
                .filter(Employee.is_deleted == False)
                .all()
            )

            # Создание PDF
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            # Устанавливаем шрифт FreeSans
            pdf.add_font('FreeSans', '', 'FreeSans.ttf', uni=True)
            pdf.set_font('FreeSans', '', 16)
            # Заголовок отчёта
            pdf.set_font('FreeSans', '', 16)
            pdf.cell(200, 10, "Отчет об обучении сотрудников", ln=True, align='C')
            pdf.ln(10)

            total_amount = 0  # Итоговая стоимость обучения

            # Заполнение данных
            pdf.set_font('FreeSans', '', 12)
            for row in data:
                last_name, first_name, surname, start, end, name_training, format_training = row
                training_cost = 0
                total_amount += training_cost

                pdf.cell(200, 10, f"{last_name} {first_name} {surname}", ln=True)
                pdf.cell(200, 10, f"Период обучения: {start} - {end}", ln=True)
                pdf.cell(200, 10, f"Курс: {name_training}", ln=True)
                pdf.cell(200, 10, f"Стоимость: {training_cost:.2f} руб.", ln=True)
                pdf.ln(5)

            # Итоговая сумма
            pdf.ln(10)
            pdf.set_font('FreeSans', '', 14)
            pdf.cell(0, 10, f"Итоговая сумма за обучение всех сотрудников: {total_amount:.2f} р.", ln=True, align='R')

            # Сохранение PDF
            pdf_output_path = f"./training_report.pdf"
            pdf.output(pdf_output_path)

            print(f"Отчет был успешно экспортирован в {pdf_output_path}")
            session.close()
            
            QMessageBox.information(self, "Успех", f"Отчет был успешно экспортирован в:\n{pdf_output_path}")
        
        except Exception as e:
            print(f"Произошла ошибка при создании отчета: {str(e)}")
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка при создании отчета: {str(e)}")

    def generate_employee_card_report(self):
        try:
            session = create_connection()

            # Загружаем сотрудников
            employees = session.query(Employee).filter(Employee.is_deleted == False).all()

            # Создаём общий PDF
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_font('FreeSans', '', 'FreeSans.ttf', uni=True)

            for employee in employees:
                # Добавляем новую страницу для каждого сотрудника
                pdf.add_page()

                # Заголовок карточки сотрудника
                pdf.set_font('FreeSans', '', 16)
                pdf.cell(200, 10, f"Карточка сотрудника: {employee.last_name} {employee.first_name} {employee.surname}", ln=True, align='C')
                pdf.ln(10)

                # Базовая информация о сотруднике
                pdf.set_font('FreeSans', '', 12)
                pdf.cell(200, 10, f"ФИО: {employee.last_name} {employee.first_name} {employee.surname or ''}", ln=True)
                pdf.cell(200, 10, f"Телефон: {employee.phone_number or 'Не указан'}", ln=True)
                pdf.cell(200, 10, f"Дата рождения: {employee.birth_date}", ln=True)
                pdf.cell(200, 10, f"СНИЛС: {employee.snils}", ln=True)
                pdf.cell(200, 10, f"ИНН: {employee.inn}", ln=True)
                pdf.cell(200, 10, f"Паспорт: {employee.passport}", ln=True)
                pdf.cell(200, 10, f"Стаж работы: {employee.work_experience}", ln=True)
                pdf.cell(200, 10, f"Семейное положение: {employee.material_status}", ln=True)
                pdf.cell(200, 10, f"Дата приёма на работу: {employee.hire_date}", ln=True)
                pdf.cell(200, 10, f"Дата увольнения: {employee.dismissal_date or 'Не уволен'}", ln=True)
                pdf.ln(5)

                # Должность сотрудника
                position = session.query(EmployeePosition).filter(EmployeePosition.employee_id == employee.id).first()
                if position:
                    pdf.cell(200, 10, f"Должность: {position.r_position.name_position}", ln=True)
                    pdf.cell(200, 10, f"Отдел: {position.department or 'Не указан'}", ln=True)
                else:
                    pdf.cell(200, 10, "Должность: Не указана", ln=True)

                pdf.ln(5)

                # Образование
                education = session.query(EmployeeEducation).filter(EmployeeEducation.employee_id == employee.id).all()
                pdf.cell(200, 10, "Образование:", ln=True)
                if education:
                    for edu in education:
                        pdf.cell(200, 10, f"- {edu.r_education.level_education} ({edu.r_education.issue_date})", ln=True)
                else:
                    pdf.cell(200, 10, "Нет данных об образовании", ln=True)

                pdf.ln(5)

                # Курсы обучения
                pdf.cell(200, 10, "Пройденные курсы:", ln=True)
                training_list = session.query(EmployeeTraining).filter(EmployeeTraining.employee_id == employee.id).all()
                if training_list:
                    for t in training_list:
                        training_name = t.r_training.name_training or "Неизвестный курс"
                        start_date = t.r_training.start_date or "Не указана"
                        end_date = t.r_training.end_date or "Не указана"
                        pdf.cell(200, 10, f"- {training_name}: {start_date} - {end_date}", ln=True)
                else:
                    pdf.cell(200, 10, "Нет пройденных курсов", ln=True)

            # Сохранение единого PDF
            pdf_output_path = "./all_employee_cards.pdf"
            pdf.output(pdf_output_path)

            print(f"Карточки сотрудников были успешно экспортированы в {pdf_output_path}.")
            session.close()

            QMessageBox.information(self, "Успех", f"Отчет был успешно экспортирован в:\n{pdf_output_path}")

        except Exception as e:
            print(f"Произошла ошибка при создании карточки сотрудника: {str(e)}")
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка при создании карточки сотрудника: {str(e)}")
        