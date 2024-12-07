from sqlalchemy import create_engine, Column, Integer, String, Date, Boolean, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, sessionmaker
from enum import Enum as PyEnum

# Создаем базовый класс
Base = declarative_base()

# Определяем Enum для department_type, training_type и education_type
class DepartmentType(PyEnum):
    HR = "HR"
    IT = "IT"
    Finance = "Finance"

class TrainingType(PyEnum):
    Online = "Онлайн"
    Offline = "Оффлайн"
    Hybrid = "Смешанное"

class EducationType(PyEnum):
    MainGeneral = "Основное общее"
    SecondaryGeneral = "Среднее общее"
    SecondaryProfessional = "Среднее профессиональное"
    Higher = "Высшее"

# Таблица для мест обучения
class TrainingPlace(Base):
    __tablename__ = 'training_place'

    id = Column(Integer, primary_key=True)
    full_name = Column(String(255))
    short_name = Column(String(255))

# Таблица для квалификаций
class Qualification(Base):
    __tablename__ = 'qualification'

    id = Column(Integer, primary_key=True)
    name_qualification = Column(String(255))
    description = Column(String)

# Таблица для специальностей
class Specialty(Base):
    __tablename__ = 'specialty'

    id = Column(Integer, primary_key=True)
    full_name_specialty = Column(String(255))
    short_name_specialty = Column(String(255))
    qualification_id = Column(Integer, ForeignKey('qualification.id'))

    # Связь с квалификацией
    qualification = relationship('Qualification')

# Таблица для документов сотрудников
class DocumentEmployee(Base):
    __tablename__ = 'document_employee'

    id = Column(Integer, primary_key=True)
    series = Column(Integer)
    number_document = Column(Integer)
    issue_date = Column(Date)
    issued_by = Column(String)

# Таблица для образования сотрудников
class Education(Base):
    __tablename__ = 'education'

    id = Column(Integer, primary_key=True)
    level_education = Column(Enum(EducationType))
    series = Column(Integer)
    number_education = Column(Integer)
    registration_number = Column(String(255))
    issue_date = Column(Date)
    specialty_id = Column(Integer, ForeignKey('specialty.id'))

    # Связь с специальностью
    specialty = relationship('Specialty')

# Таблица для должностей сотрудников
class PositionEmployee(Base):
    __tablename__ = 'position_employee'

    id = Column(Integer, primary_key=True)
    name_position = Column(String(255))
    responsibilities = Column(String)

# Таблица для сотрудников
class Employee(Base):
    __tablename__ = 'employee'

    id = Column(Integer, primary_key=True)
    last_name = Column(String(255))
    first_name = Column(String(255))
    surname = Column(String(255))
    phone_number = Column(String(255))
    birth_date = Column(Date)
    snils = Column(String(255))
    inn = Column(String(255))
    passport = Column(String(255))
    work_experience = Column(Integer)
    material_status = Column(Boolean)
    hire_date = Column(Date)
    dismissal_date = Column(Date)
    is_deleted = Column(Boolean, default=False)

# Связующая таблица для должностей сотрудников
class EmployeePosition(Base):
    __tablename__ = 'employee_position'

    id = Column(Integer, primary_key=True)
    position_id = Column(Integer, ForeignKey('position_employee.id'))
    employee_id = Column(Integer, ForeignKey('employee.id'))
    department = Column(Enum(DepartmentType))

    # Связи с сотрудниками и должностями
    position = relationship('PositionEmployee')
    employee = relationship('Employee')

# Таблица для тренингов
class Training(Base):
    __tablename__ = 'training'

    id = Column(Integer, primary_key=True)
    name_training = Column(String(255))
    type_training = Column(Enum(TrainingType))
    start_date = Column(Date)
    end_date = Column(Date)
    format_training = Column(Boolean)
    training_place_id = Column(Integer, ForeignKey('training_place.id'))

    # Связь с местом проведения тренинга
    training_place = relationship('TrainingPlace')

# Связующая таблица для обучения сотрудников
class EmployeeTraining(Base):
    __tablename__ = 'employee_training'

    id = Column(Integer, primary_key=True)
    training_id = Column(Integer, ForeignKey('training.id'))
    employee_id = Column(Integer, ForeignKey('employee.id'))
    completed = Column(Boolean)
    document_path = Column(String(255))

    # Связи с сотрудниками и тренингами
    training = relationship('Training')
    employee = relationship('Employee')

# Связующая таблица для образования сотрудников
class EmployeeEducation(Base):
    __tablename__ = 'employee_education'

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey('employee.id'))
    education_id = Column(Integer, ForeignKey('education.id'))

    # Связи с сотрудниками и образованием
    employee = relationship('Employee')
    education = relationship('Education')

def create_connection():

    engine = create_engine(f"postgresql://postgres@localhost:5432/miniapp2", echo = True) # Создаем объект Engine для подключения к базе данных
    Base.metadata.create_all(engine) # Создаем таблицу users в базе данных, если она еще не существует
    Session = sessionmaker(bind=engine) # Создаем фабрику сессий
    session = Session(bind = engine) # Создаем сессию для работы с базой данных
    return session