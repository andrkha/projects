CREATE PROCEDURE Обновить_Стоимость
  @договор_id INT,
  @скидка DECIMAL(3,2)
AS
  UPDATE квитанции
  SET сумма = сумма * (1 - @скидка)
  WHERE договор_id = @договор_id;