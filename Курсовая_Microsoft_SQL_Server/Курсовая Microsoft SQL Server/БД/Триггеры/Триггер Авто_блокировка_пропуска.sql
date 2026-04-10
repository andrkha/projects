CREATE TRIGGER Авто_Блокировка_Пропуска
ON задолженности
AFTER INSERT, UPDATE
AS
  UPDATE студенты
  SET статус_пропуска = 0
  WHERE студент_id IN (
    SELECT d.студент_id 
    FROM inserted i
    JOIN договоры d ON i.договор_id = d.договор_id
    WHERE i.статус = 'непогашенная'
  );