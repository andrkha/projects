
CREATE PROCEDURE Добавить_Квитанцию
  @договор_id INT,
  @сумма DECIMAL(10,2),
  @месяц_оплаты DATE
AS
BEGIN
    DECLARE @max_id INT;
    
    -- Находим максимальный существующий ID
    SELECT @max_id = ISNULL(MAX(квитанция_id), 0) FROM квитанции;
    
    -- Вставляем запись с новым ID
    INSERT INTO квитанции (квитанция_id, договор_id, сумма, месяц_оплаты, дата_оплаты)
    VALUES (@max_id + 1, @договор_id, @сумма, @месяц_оплаты, GETDATE());
END;