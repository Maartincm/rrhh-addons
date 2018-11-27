CREATE DEFINER=`root`@`%` TRIGGER `RRHH`.`fichada_AFTER_INSERT` AFTER INSERT ON `fichada` FOR EACH ROW
BEGIN
    
    UPDATE dispositivo
		SET ultima_conexion = NOW()
				WHERE id = NEW.id_dispositivo;

END