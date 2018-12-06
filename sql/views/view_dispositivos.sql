select
    `RRHH`.`dispositivo`.`nombre` AS `Reloj`,
    count(`RRHH`.`fichada`.`id_dispositivo`) AS `CantFichadas`,
    `RRHH`.`dispositivo`.`ultima_conexion` AS `UltConexion`,
    IF(DATEDIFF(`RRHH`.`dispositivo`.`ultima_conexion`, NOW())<-1, 1,0) AS `Alarma`
from
    (`RRHH`.`dispositivo`
join `RRHH`.`fichada` on
    ((`RRHH`.`dispositivo`.`id` = `RRHH`.`fichada`.`id_dispositivo`)))
group by
    `RRHH`.`dispositivo`.`nombre`
order by
    count(`RRHH`.`fichada`.`id_dispositivo`) desc;
