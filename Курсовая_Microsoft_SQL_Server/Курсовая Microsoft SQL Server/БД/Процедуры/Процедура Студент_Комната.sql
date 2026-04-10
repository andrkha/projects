CREATE PROCEDURE Студент_Комната
  @student_id INT
AS
  SELECT 
    s.фамилия + ' ' + s.имя AS студент,
    r.номер AS комната,
    h.номер AS общежитие,
    lc.название AS льгота,
    lc.коэффициент_скидки
  FROM 
    студенты s
    JOIN договоры d ON s.студент_id = d.студент_id
    JOIN комнаты r ON d.комната_id = r.комната_id
    JOIN общежития h ON r.общежитие_id = h.общежитие_id
    LEFT JOIN льготы l ON s.студент_id = l.студент_id
    LEFT JOIN льготные_категории lc ON l.льготная_категория_id = lc.льготная_категория_id
  WHERE 
    s.студент_id = @student_id;