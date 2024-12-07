--create type department_type as enum ('HR', 'IT', 'Finance');
--create type training_type as enum ('Онлайн', 'Оффлайн', 'Смешанное');
--create type education_type as enum ('Основное общее', 'Среднее общее', 'Среднее профессиональное', 'Высшее');

-- Создание таблицы мест обучения
create table training_place (
	id serial primary key,
	full_name varchar(255),
	short_name varchar(255)
);

-- Создание таблицы квалификаций
create table qualification (
	id serial primary key,
	name_qualification varchar(255),
	description text
);

-- Создание таблицы специальностей
create table specialty (
	id serial primary key,
	full_name_specialty varchar(255),
	short_name_specialty varchar(255),
	qualification_id int references qualification(id)
);

-- Создание таблицы документов
create table document_employee (
	id serial primary key,
	series int,
	number_document int,
	issue_date date,
	issued_by text
);

-- Создание таблицы образования
create table education (
	id serial primary key,
	level_education education_type,
	series int,
	number_education int,
	registration_number varchar(255),
	issue_date date,
	specialty_id int references specialty(id)

);

-- Создание таблицы должностей
create table position (
	id serial primary key,
	name_position varchar(255),
	responsibilities text
);

-- Создание таблицы сотрудников
create table employee (
	id serial primary key,
	last_name varchar(255),
	first_name varchar(255),
	surname varchar(255),
	phone_number varchar(255),
	birth_date date,
	snils varchar(255),
	inn varchar(255),
	passport varchar(255),
	work_experience int,
	material_status boolean,
	hire_date date,
	dismissal_date date,
	is_deleted boolean default false 
);

-- Создание таблицы должностей сотрудников (связующая таблица)
create table employee_position (
	id serial primary key,
	position_id int references position(id),
	employee_id int references employee(id),
	department department_type
);

-- Создание таблицы обучения
create table training (
	id serial primary key,
	name_training varchar(255),
	type_training training_type,
	start_date date,
	end_date date,
	format_training boolean,
	training_place_id int references training_place(id)
);

-- Создание таблицы обучения сотрудников (связующая таблица)
create table employee_training (
	id serial primary key,
	training_id int references training(id),
	employee_id int references employee(id),
	completed boolean,
	document_path varchar(255)
);

-- Создание таблицы образования сотрудников (связующая таблица)
create table employee_education (
	id serial primary key,
	employee_id int references employee(id),
	education_id int references education(id)
);