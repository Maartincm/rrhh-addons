SELECT RRHH.fichada.*
FROM RRHH.fichada
LEFT JOIN RRHH.empleado ON (fichada.numero_legajo = empleado.id)
WHERE RRHH.empleado.id IS NULL
ORDER BY numero_legajo;

SELECT DISTINCT(RRHH.fichada.numero_legajo)
FROM RRHH.fichada
LEFT JOIN RRHH.empleado ON (fichada.numero_legajo = empleado.id)
WHERE RRHH.empleado.id IS NULL
GROUP BY numero_legajo
ORDER BY numero_legajo;