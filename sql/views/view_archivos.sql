CREATE 
    ALGORITHM = UNDEFINED 
    DEFINER = `root`@`%` 
    SQL SECURITY DEFINER
VIEW `RRHH`.`archivo_view` AS
    SELECT 
        `RRHH`.`archivo`.`id` AS `ID_Archivo`,
        `RRHH`.`archivo`.`nombre` AS `Nombre`,
        COUNT(`RRHH`.`fichada`.`id`) AS `Cantidad`,
        `RRHH`.`archivo`.`cargado_mysql` AS `Fecha_Mysql`,
        `RRHH`.`archivo`.`cargado_odoo` AS `Fecha_Odoo`
    FROM
        (`RRHH`.`archivo`
        JOIN `RRHH`.`fichada` ON ((`RRHH`.`archivo`.`id` = `RRHH`.`fichada`.`id_archivo`)))
    GROUP BY `RRHH`.`archivo`.`id` , `RRHH`.`archivo`.`nombre` , `RRHH`.`archivo`.`cargado_mysql` , `RRHH`.`archivo`.`cargado_odoo`
    ORDER BY `Fecha_Mysql` DESC