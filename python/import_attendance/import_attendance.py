#!/usr/bin/env python3

import argparse
import ast
import configparser
import functools
import logging
import os
from datetime import datetime, timezone
from importlib import machinery as ModuleImporter
from pprint import pformat as pf

import MySQLdb
from MySQLdb import cursors
import odoorpc
from tzlocal import get_localzone


_logger = logging.getLogger('import_attendances_to_odoo')

DTF = "%Y-%m-%d %H:%M:%S"


def dictfetchall(self):
    fetch = self.fetchall()
    if not fetch or not fetch[0]:
        return {}
    return [{self.description[index][0]: val for
             index, val in enumerate(line)} for line in fetch]


cursors.Cursor.dictfetchall = dictfetchall


def configure_logger(filename, level='info'):

    log_f = '%(asctime)s |%(levelname)-5.5s|: %(message)s'
    log_formatter = logging.Formatter(log_f)

    log_handler = logging.StreamHandler()
    log_handler.setFormatter(log_formatter)

    file_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        filename)
    log_file_handler = logging.FileHandler(file_path)
    log_file_handler.setFormatter(log_formatter)

    _logger.addHandler(log_handler)
    _logger.addHandler(log_file_handler)

    if level.lower() == 'info':
        _logger.setLevel('INFO')
    else:
        _logger.setLevel('DEBUG')


def local_datetime():
    local_tz = get_localzone()
    utc_datetime = datetime.utcnow().replace(tzinfo=timezone.utc)
    return utc_datetime.astimezone(tz=local_tz)


class ConfigFileReader(configparser.ConfigParser):

    def __init__(self, filename, *args, **kwargs):
        self.filename = filename
        super().__init__(*args, **kwargs)
        _logger.info("Reading Configuration File %s" % self.filename)
        file_read = self.read(self.filename)
        if not file_read:
            full_file_path = os.path.join(
                os.path.abspath(os.path.curdir),
                os.path.dirname(__file__),
                self.filename)
            file_read = self.read(full_file_path)
            if not file_read:
                raise IOError(
                    "Configuration File '%s' was not found" % self.filename)

    def validate(self):
        sections = self.sections()
        required_sections = ['odoo', 'mysql']
        _logger.debug("Validating Configuration File %s" % self.filename)
        for rs in required_sections:
            if rs not in sections:
                raise ValueError(
                    "'%s' section is required in the config file" % rs)

        odoo_required_keys = ['host', 'port', 'db', 'user', 'password',
                              'iod_path']
        for key in odoo_required_keys:
            if key not in self['odoo']:
                raise ValueError(
                    ("'%s' key is required in the 'odoo' section of " +
                     "the config file") % key)

        mysql_required_keys = ['username', 'password', 'database', 'host']
        for key in mysql_required_keys:
            if key not in self['mysql']:
                raise ValueError(
                    ("'%s' key is required in the 'mysql' section of " +
                     "the config file") % key)


class CustomArgumentParser(argparse.ArgumentParser):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.configure()

    def configure(self):
        self.add_argument('-c', '--config-file',
                          help='Configuration File (INI)')
        self.add_argument('-o', '--output-file',
                          help='Logging Output File')
        self.add_argument('-v', '--verbose', action="store_true",
                          help='Show Debug Messages')
        self.args = self.parse_args()


def cr(fnct):
    @functools.wraps(fnct)
    def wrapped_cr(obj, *args, **kwargs):
        if not hasattr(obj, 'connection'):
            raise ValueError(
                ("Connection not established when trying to get cursor " +
                 "for Mysql Database"))
        cr = obj.connection.cursor()
        res = fnct(obj, cr, *args, **kwargs)
        obj.connection.commit()
        return res
    return wrapped_cr


class MysqlConnector():

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.validate_fields()
        _logger.info("Connecting to Mysql")
        _logger.debug(
            ("MYSQL: Connection Information:\n\tHost: %s\n\tDatabase: %s" +
             "\n\tUsername: %s") % (self.host, self.database, self.username))
        self.connection = MySQLdb.connect(
            host=self.host, user=self.username, passwd=self.password,
            db=self.database,
            port=(hasattr(self, 'port') and int(self.port)) or '3306')

    def validate_fields(self):
        required = ['host', 'database', 'username', 'password']
        for f in required:
            if not hasattr(self, f):
                raise ValueError(
                    ("'%s' parameter is required for MysqlConnector") % f)

    def get_file_ids(self, cr):
        query = """
        SELECT
            ar.id file_id,
            ar.nombre file_name
        FROM archivo ar
        WHERE cargado_odoo IS NULL
        """
        cr.execute(query)
        files = cr.dictfetchall()
        file_ids = [single_file['file_id'] for single_file in files]
        return file_ids

    def get_attendances_from_files(self, cr, file_ids):
        if not file_ids:
            return []
        query = """
        SELECT
            DATE_ADD(fi.fecha_hora, INTERVAL 3 HOUR) att_datetime,
            fi.numero_legajo att_partner_ref,
            CASE id_tipo_evento
                WHEN 0 THEN 'Entrada'
                ELSE 'Salida'
            END AS event_type,
            di.id AS clock_id,
            di.nombre AS clock_name,
            fi.id_archivo AS att_file_id
        FROM fichada fi
        JOIN dispositivo di
            ON di.id = fi.id_dispositivo
        WHERE id_archivo IN %(file_ids)s
        """
        query_vals = {
            'file_ids': tuple(file_ids),
        }
        cr.execute(query, query_vals)
        attendances = cr.dictfetchall()
        return attendances

    @cr
    def mark_file_as_read(self, cr, file_ids):
        load_time = local_datetime().strftime(DTF)
        query = """
        UPDATE archivo
        SET
            cargado_odoo = %(load_time)s
        WHERE id = %(file_id)s
        """
        executed_count = 0
        for file_id in file_ids:
            query_vals = {
                'load_time': load_time,
                'file_id': file_id,
            }
            executed_count += cr.execute(query, query_vals)
        return executed_count

    @cr
    def get_data(self, cr):
        _logger.info("MYSQL: Fetching Attendance Data from MySQL")
        file_ids = self.get_file_ids(cr)
        _logger.debug(("MYSQL: Found %s files:\n\t%s") %
                      (len(file_ids), pf(file_ids)))
        attendances = self.get_attendances_from_files(cr, file_ids)
        _logger.debug(("MYSQL: Found %s attendances") %
                      (len(attendances)))
        result = {
            'attendances': attendances,
            'file_ids': file_ids,
        }
        return result


class OdooConnector():

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.validate_fields()
        self.prepare_connection()

    def validate_fields(self):
        if not hasattr(self, 'host'):
            raise ValueError(
                "'host' parameter is required for OdooConnector")
        self._connection_mode = 'odoorpc'
        if self.host in ['localhost', '127.0.0.1'] and (
                hasattr(self, 'local') and self.local and
                '.' not in self.local):
            try:
                cond = ast.literal_eval(self.local)
            except BaseException:
                pass
            else:
                if cond:
                    if not hasattr(self, 'iod_path'):
                        raise ValueError(
                            ("'iod_path' parameter is required for " +
                             "OdooConnector when the host is the same " +
                             "machine or the 'local' option is set"))
                    else:
                        self._connection_mode = 'iod'

    def prepare_connection(self):
        fnct = getattr(self, "prepare_connection_for_%s" %
                       self._connection_mode)
        res = fnct()
        return res

    def prepare_connection_for_iod(self):
        _logger.info("Connection to Odoo via IOD")
        if os.path.isabs(self.iod_path):
            iod_path = self.iod_path
        else:
            iod_path = os.path.join(
                os.path.dirname(__file__),
                self.iod_path)
        loader = ModuleImporter.SourceFileLoader(
            "iod", iod_path)
        iod = loader.load_module()
        self.iod = iod

    def prepare_connection_for_odoorpc(self):
        _logger.info("Connection to Odoo via OdooRPC")
        protocol = 'jsonrpc'
        version = '11.0'
        if hasattr(self, 'ssl') and self.ssl and '.' not in self.ssl:
            try:
                cond = ast.literal_eval(self.ssl)
            except BaseException:
                pass
            else:
                if cond:
                    protocol = 'jsonrpc+ssl'
        if hasattr(self, 'version') and self.version in \
                ['7.0', '8.0', '9.0', '10.0', '11.0', '12.0']:
            version = self.version
        odoo = odoorpc.ODOO(self.host, port=self.port, version=version,
                            protocol=protocol)
        odoo.login(self.db, self.user, self.password)
        self.odoorpc = odoo

    def import_attendance_from_env(self, env, data, new_api=True):
        employee_model = env['hr.employee']
        clock_model = env['hr.attendance.clock']
        attendance_model = env['hr.attendance.middle.import']

        if new_api:
            new_atts = env['hr.attendance.middle.import']
        else:
            new_atts = []
        for attendance in data:
            clock_name = attendance.get('clock_name')
            clock = clock_model.search([
                ('name', '=', clock_name)])
            if not clock:
                _logger.debug(("ODOO: Creating Clock: %s") %
                              (clock_name))
                clock = clock_model.create({
                    'name': clock_name,
                })
            partner_ref = attendance.get('att_partner_ref')
            employee = employee_model.search([('otherid', '=', partner_ref)])
            if len(employee) != 1:
                _logger.warning(("ODOO: Employee with barcode '%s' was not " +
                                 "found") % (partner_ref))
                continue
            if not new_api:
                employee = employee_model.browse(employee[0])
                clock = clock_model.browse(
                    isinstance(clock, list) and clock[0] or clock)
            attendance_vals = {
                'employee_id': employee.id,
                'datetime': attendance.get('att_datetime').strftime(DTF),
                'warehouse_id': 1,
                'clock_id': clock.id,
            }
            _logger.debug(("ODOO: Creating Entry for Employee '%s' with " +
                           "values:\n\t%s") %
                          (employee.name, pf(attendance_vals)))
            if new_api:
                new_atts += attendance_model.create(attendance_vals)
            else:
                new_atts.append(attendance_model.create(attendance_vals))
            if hasattr(env, 'cr') and hasattr(env.cr, 'commit'):
                env.cr.commit()
        return new_atts

    def import_attendance_by_iod(self, data):
        _logger.debug("ODOO: Importing attendances via IOD")
        env = self.iod.IOD.env
        res = self.import_attendance_from_env(env, data, new_api=True)
        self.iod.IOD.session.close()
        return res

    def import_attendance_by_odoorpc(self, data):
        _logger.debug("ODOO: Importing attendances via ODOORPC")
        env = self.odoorpc.env
        return self.import_attendance_from_env(env, data, new_api=False)

    def import_attendance(self, data):
        _logger.info("Beginning Import of Attendances in Odoo")
        fnct = getattr(self, "import_attendance_by_%s" % self._connection_mode)
        res = fnct(data)
        return res


def timedelta_strftime(delta):
    res_str = ""
    remain, seconds = divmod(delta.seconds, 60)
    res_str += "%s seconds" % str(seconds).zfill(2)
    if remain:
        remain, minutes = divmod(remain, 60)
        res_str = "%s minutes, " % str(minutes).zfill(2) + res_str
        if remain:
            zero, hours = divmod(remain, 24)
            res_str = "%s hours, " % str(hours).zfill(2) + res_str
    if delta.days:
        res_str = "%s days, " % delta.days + res_str
    return res_str


if __name__ == '__main__':
    start = local_datetime()
    ArgParser = CustomArgumentParser()
    configure_logger(ArgParser.args.output_file or 'fichada.log',
                     level=ArgParser.args.verbose and 'debug' or 'info')
    _logger.info("Attendance Import Begun at %s" % start.strftime(DTF))
    ConfigFile = ConfigFileReader(ArgParser.args.config_file or 'config.ini')
    ConfigFile.validate()

    Mysql = MysqlConnector(**ConfigFile['mysql'])
    Odoo = OdooConnector(**ConfigFile['odoo'])

    mysql_data = Mysql.get_data()
    _logger.info("MYSQL: Closing connection to MySQL")

    attendances = Odoo.import_attendance(mysql_data.get('attendances'))

    file_ids = mysql_data.get('file_ids')
    Mysql.mark_file_as_read(file_ids)
    _logger.debug(("MYSQL: Marked %s files as read:\n\t%s") %
                  (len(file_ids), pf(file_ids)))

    Mysql.connection.close()

    end = local_datetime()
    delta = end - start
    delta_str = timedelta_strftime(delta)
    _logger.info(("Attendance Import Finished at %s\nTime Elapsed: %s" +
                  "\nAttendances Created: %s\n\n") %
                 (end.strftime(DTF), delta_str, len(attendances)))
