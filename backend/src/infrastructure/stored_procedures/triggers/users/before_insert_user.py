before_insert_user = """
DELIMITER //

CREATE TRIGGER before_insert_user
BEFORE INSERT ON users FOR EACH ROW
BEGIN
    -- пока что просто обновляем время пользователя, впоследствии надо будет сохранять изменения в отдельную таблицу
    SET NEW.created_at = NOW();
    SET NEW.updated_at = NOW();
    
END//

DELIMITER ;
"""