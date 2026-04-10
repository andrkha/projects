CREATE TRIGGER Лог_Изменений_Договора
ON договоры
AFTER UPDATE
AS
  INSERT INTO логи_изменений (действие, договор_id, дата_изменения)
  SELECT 'Обновление', договор_id, GETDATE() FROM inserted;