CREATE TRIGGER Контроль_Даты_Договора
ON договоры
AFTER INSERT, UPDATE
AS
  IF EXISTS (SELECT * FROM inserted WHERE дата_начала < дата_заключения)
  BEGIN
    RAISERROR('Дата начала проживания не может быть раньше даты заключения договора!', 16, 1);
    ROLLBACK TRANSACTION;
  END;