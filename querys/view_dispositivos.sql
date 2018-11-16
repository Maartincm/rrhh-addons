SELECT 
	dispositivo.nombre AS Reloj,
    count(fichada.id_dispositivo) AS CantFichadas,
    dispositivo.ultima_conexion AS UltConexion
FROM
	RRHH.dispositivo 
INNER JOIN RRHH.fichada ON (dispositivo.id = fichada.id_dispositivo)
GROUP BY dispositivo.nombre
ORDER BY count(fichada.id_dispositivo) DESC;
