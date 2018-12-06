CREATE
OR REPLACE
VIEW `RRHH`.`interfaz_view` AS select
    `RRHH`.`control_interfaz_odoo`('mysql') AS `MysqlPend`,
    `RRHH`.`control_interfaz_odoo`('odoo') AS `OdoolPend`,
    (`RRHH`.`control_interfaz_odoo`('mysql') - `RRHH`.`control_interfaz_odoo`('odoo')) AS `Diferencia`