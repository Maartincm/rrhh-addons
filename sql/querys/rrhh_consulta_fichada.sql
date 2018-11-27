SELECT
	dispositivo.nombre AS Reloj,
	fichada.fecha_hora AS Fecha,
    empleado.nombre AS Nombre,
    empleado.apellido AS Apellido,
    fichada.numero_legajo AS Legajo,
    tipo_evento.nombre AS Evento
 FROM fichada
	INNER JOIN empleado ON (fichada.numero_legajo = empleado.numero_legajo)
    INNER JOIN tipo_evento ON (fichada.id_tipo_evento = tipo_evento.id)
    INNER JOIN dispositivo ON (dispositivo.id = fichada.id_dispositivo)
ORDER BY dispositivo.nombre, fichada.fecha_hora;