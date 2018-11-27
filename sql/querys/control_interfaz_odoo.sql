CREATE DEFINER=`root`@`%` FUNCTION `RRHH`.`control_interfaz_odoo`(plataforma VARCHAR(10)) RETURNS int(11)
    DETERMINISTIC
BEGIN
    DECLARE value INT;
   	IF (plataforma = "odoo") THEN
   		SELECT COUNT(*) INTO value FROM RRHH.archivo WHERE cargado_odoo IS NULL;
   	ELSEIF (plataforma = "mysql") THEN
   		SELECT COUNT(*) INTO value FROM RRHH.archivo WHERE cargado_mysql IS NULL;
   	ELSE
   		SET value = 0;
   	END IF;
    
 RETURN (value);
END