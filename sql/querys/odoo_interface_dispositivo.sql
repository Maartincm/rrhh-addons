USE RRHH;
SELECT 
	DATE_ADD(fichada.fecha_hora, INTERVAL 3 HOUR) AS Fecha,
	fichada.numero_legajo AS Legajo,
	CASE fichada.id_tipo_evento
		WHEN 0 THEN 'Entrada'
	   	WHEN 1 THEN 'Salida'
	   	WHEN 2 THEN 'Salida'
	END AS Evento,
	dispositivo.nombre AS Reloj
FROM fichada 
	INNER JOIN dispositivo 
		ON (fichada.id_dispositivo = dispositivo.id)
WHERE id_archivo = 403;