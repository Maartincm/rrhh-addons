CREATE DEFINER=`root`@`%` TRIGGER `RRHH`.`fichada_AFTER_INSERT` AFTER INSERT ON `fichada` FOR EACH ROW
BEGIN

	DECLARE cantidadFichadas INTEGER DEFAULT 0;
    
    /* Selecionando cantidad de registros */
    SELECT cantidad_fichada
		INTO cantidadFichadas
			FROM dispositivo
				WHERE id = NEW.id_dispositivo;

	SET cantidadFichadas = cantidadFichadas + 1;
    
    UPDATE dispositivo
		SET cantidad_fichada = cantidadFichadas,
			ultima_conexion = NOW()
				WHERE id = NEW.id_dispositivo;

END