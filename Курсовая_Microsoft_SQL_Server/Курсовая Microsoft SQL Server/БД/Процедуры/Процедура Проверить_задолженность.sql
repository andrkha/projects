CREATE PROCEDURE Проверить_Задолженность
  @студент_id INT
AS
  DECLARE @долг DECIMAL(10,2);
  SELECT @долг = SUM(сумма) 
  FROM задолженности 
  WHERE договор_id IN (SELECT договор_id FROM договоры WHERE студент_id = @студент_id);
  
  IF @долг > 0
    UPDATE студенты SET статус_пропуска = 0 WHERE студент_id = @студент_id;