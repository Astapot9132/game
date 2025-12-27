before_update_user = """
DELIMITER //

CREATE TRIGGER before_update_user
BEFORE INSERT ON users FOR EACH ROW
BEGIN
    -- пока что просто обновляем время пользователя, впоследствии надо будет сохранять изменения в отдельную таблицу
    SET NEW.created_at = OLD.created_at;
    SET NEW.updated_at = NOW();

END//

DELIMITER ;
"""