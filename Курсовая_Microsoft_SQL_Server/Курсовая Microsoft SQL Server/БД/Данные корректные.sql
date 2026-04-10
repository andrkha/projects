DROP DATABASE Общежитие 
CREATE DATABASE Общежитие 
GO
USE Общежитие 

-- Создание таблицы Типы льгот
CREATE TABLE льготные_категории (
    льготная_категория_id INT PRIMARY KEY CHECK (льготная_категория_id BETWEEN 1 AND 100),
    название NVARCHAR(100) NOT NULL,
    описание NVARCHAR(MAX),
    коэффициент_скидки DECIMAL(3,2) NOT NULL CHECK (коэффициент_скидки BETWEEN 0.0 AND 1.0),
    подтверждающий_документ NVARCHAR(100) NOT NULL
);

-- Создание таблицы Студенты
CREATE TABLE студенты (
    студент_id INT PRIMARY KEY CHECK (студент_id BETWEEN 1 AND 100),
    телефон NVARCHAR(20) NOT NULL UNIQUE CHECK (телефон LIKE '+7[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]'),
    имя NVARCHAR(50) NOT NULL,
    фамилия NVARCHAR(50) NOT NULL,
    статус_пропуска BIT NOT NULL DEFAULT 1
);

-- Создание таблицы Льготы
CREATE TABLE льготы (
    льгота_id INT PRIMARY KEY CHECK (льгота_id BETWEEN 1 AND 100),
    студент_id INT NOT NULL REFERENCES студенты(студент_id),
    льготная_категория_id INT NOT NULL REFERENCES льготные_категории(льготная_категория_id),
    дата_начала DATE NOT NULL,
    дата_окончания DATE NULL,
    CONSTRAINT даты_льгот CHECK (дата_окончания IS NULL OR дата_окончания >= дата_начала)
);

-- Создание таблицы Общежития
CREATE TABLE общежития (
    общежитие_id INT PRIMARY KEY CHECK (общежитие_id BETWEEN 1 AND 100),
    номер NVARCHAR(10) NOT NULL UNIQUE,
    адрес NVARCHAR(MAX) NOT NULL,
    количество_комнат INT NOT NULL CHECK (количество_комнат > 0)
);

-- Создание таблицы Комнаты
CREATE TABLE комнаты (
    комната_id INT PRIMARY KEY CHECK (комната_id BETWEEN 1 AND 100),
    номер NVARCHAR(10) NOT NULL,
    общежитие_id INT NOT NULL REFERENCES общежития(общежитие_id),
    вместимость INT NOT NULL CHECK (вместимость BETWEEN 1 AND 6),
    стоимость DECIMAL(10,2) NOT NULL CHECK (стоимость > 0),
    этаж INT NOT NULL CHECK (этаж BETWEEN 1 AND 10),
    CONSTRAINT уникальный_номер_комнаты UNIQUE (номер, общежитие_id)
);

-- Создание таблицы Договоры
CREATE TABLE договоры (
    договор_id INT PRIMARY KEY CHECK (договор_id BETWEEN 1 AND 100),
    студент_id INT NOT NULL REFERENCES студенты(студент_id),
    комната_id INT NOT NULL REFERENCES комнаты(комната_id),
    дата_заключения DATE NOT NULL DEFAULT GETDATE(),
    дата_начала DATE NOT NULL,
    дата_окончания DATE NULL,
    CONSTRAINT даты_договора CHECK (
        дата_начала >= дата_заключения AND 
        (дата_окончания IS NULL OR дата_окончания >= дата_начала)
    )
);

-- Создание таблицы Квитанции
CREATE TABLE квитанции (
    квитанция_id INT PRIMARY KEY CHECK (квитанция_id BETWEEN 1 AND 100),
    договор_id INT NOT NULL REFERENCES договоры(договор_id),
    сумма DECIMAL(10,2) NOT NULL CHECK (сумма > 0),
    месяц_оплаты DATE NOT NULL,
    дата_оплаты DATE NOT NULL,
    дата_просрочки DATE NULL
);

-- Создание таблицы Задолженности
CREATE TABLE задолженности (
    задолженность_id INT CHECK (задолженность_id BETWEEN 1 AND 100),
    договор_id INT NOT NULL REFERENCES договоры(договор_id),
    сумма DECIMAL(10,2) NOT NULL CHECK (сумма > 0),
    дата_возникновения DATE NOT NULL DEFAULT GETDATE(),
    дата_погашения DATE NULL,
    статус NVARCHAR(20) NOT NULL DEFAULT 'непогашенная' CHECK (статус IN ('непогашенная', 'частично погашенная', 'погашенная'))
);