
from PySide6.QtWidgets import QDialog, QFormLayout, QComboBox,  QDialogButtonBox
from PySide6.QtCore import Qt, QDate
from modules import create_connection, Training, EmployeeTraining


class AddTrainingDialog(QDialog):
    def __init__(self, employee_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить обучение")
        self.setGeometry(100, 100, 400, 300)

        self.layout = QFormLayout()

        # Выбор тренинга
        self.training_combo = QComboBox(self)
        session = create_connection()
        trainings = session.query(Training).all()
        for training in trainings:
            self.training_combo.addItem(training.name_training, training.id)

        self.layout.addRow("Тренинг", self.training_combo)

        # Кнопки для добавления
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.buttons.accepted.connect(self.save_training)
        self.buttons.rejected.connect(self.reject)

        self.layout.addWidget(self.buttons)
        self.setLayout(self.layout)

    def save_training(self):
        session = create_connection()
        training_id = self.training_combo.currentData()
        employee_training = EmployeeTraining(employee_id=self.employee_id, training_id=training_id, completed=False)
        session.add(employee_training)
        session.commit()
        session.close()
        self.accept()