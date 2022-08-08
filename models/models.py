# -*- coding: utf-8 -*-
from odoo import models, fields, api
import sys
import datetime
from datetime import timedelta
import os
sys.path.append("zk")
from zk import ZK, const
import time
import random

connect = None

class mb_uface202(models.Model):
    _name = 'mb_uface202.device'
    _inherit = 'hr.attendance'
    _description = 'mb_uface202.device'


    name = fields.Char()
    ip = fields.Char()
    port = fields.Integer()
    position = fields.Char()
    company = fields.Char()

    def job(self):
        print("I'm working...")

    def calling(self):
        print(mb_uface202.name)
        conn = None
        zk = ZK(self[0].ip, port=self[0].port, timeout=5, password=0, force_udp=False, ommit_ping=False)

        try:
            print ('Connecting to device ...')
            conn = zk.connect()
            print ('Disabling device ...')
            conn.disable_device()
            print ('Firmware Version: : {}'.format(conn.get_firmware_version()))
            # print '--- Get User ---'
            users = conn.get_users()
            for user in users:
                privilege = 'User'
                if user.privilege == const.USER_ADMIN:
                    privilege = 'Admin'
                print('- UID #{}'.format(user.uid))
                print('  Name       : {}'.format(user.name))
                print('  Privilege  : {}'.format(privilege))
                print('  Password   : {}'.format(user.password))
                print('  Group ID   : {}'.format(user.group_id))
                print('  User  ID   : {}'.format(user.user_id))

            print ("Voice Test ...")
            conn.test_voice()
            print ('Enabling device ...')
            conn.enable_device()
        except Exception as e:
            print ("Process terminate : {}".format(e))

            if conn:
                conn.disconnect()

    def restart(self):
        zk = ZK(self[0].ip, port=self[0].port, timeout=5, password=0, force_udp=False, ommit_ping=False)
        try:
            connect = zk.connect()
            print("restart Device...")
            connect.restart()
        except Exception as e:
            print("Process terminate : {}".format(e))

    def poweroff(self):
        zk = ZK(self[0].ip, port=self[0].port, timeout=5, password=0, force_udp=False, ommit_ping=False)
        try:
            connect = zk.connect()
            print("poweroff Device...")
            connect.poweroff()
        except Exception as e:
            print("Process terminate : {}".format(e))

    def get(self):
        zk = ZK(self[0].ip, port=self[0].port, timeout=5, password=0, force_udp=False, ommit_ping=False)
        connect = zk.connect()
        atts = connect.get_attendance()
        for att in atts:
            query = """INSERT INTO mb_uface202_log(name,uid,os_time,zk_time)values(%s,%s,%s,%s)"""
            self._cr.execute(query,
                             (str(att.user_id), int(att.user_id), str(datetime.datetime.now())[:-7],
                              str(att.timestamp - timedelta(hours=3, minutes=30))))
            query = """INSERT INTO mb_uface202_pool(name,uid,os_time,zk_time)values(%s,%s,%s,%s)"""
            self._cr.execute(query,
                             (str(att.user_id), int(att.user_id), str(datetime.datetime.now())[:-7],
                              str(att.timestamp - timedelta(hours=3, minutes=30))))
            self.separation()
        connect.clear_attendance()

    @api.depends('check_in', 'check_out')
    def _compute_worked_hours(self):
        for attendance in self:
            if attendance.check_out:
                delta = attendance.check_out - attendance.check_in
                attendance.worked_hours = delta.total_seconds() / 3600.0
            else:
                attendance.worked_hours = False

    def separation(self):
        query = """SELECT * FROM mb_uface202_pool;"""
        self._cr.execute(query)
        res = self._cr.fetchall()
        for q in res:
            self._cr.execute("UPDATE mb_uface202_log SET done = true WHERE uid = " + str(q[2]) + ";")

        self._cr.execute(
            "SELECT * from hr_attendance  WHERE employee_id =" + str(q[2]) + " order by write_date desc limit 1")
        rows = self._cr.fetchall()
        print(rows)

        if rows == []:
            sqlquery = "INSERT INTO hr_attendance(employee_id,check_in,check_out,worked_hours,create_uid,create_date,write_uid,write_date)values(%s,%s,%s,%s,%s,%s,%s,%s)"
            self._cr.execute(sqlquery, (int(str(q[2])), str(q[4]), None, int(0), int(2),
                                        str('2020-07-16 18:27:12'), int(2),
                                        str(datetime.datetime.now())[:-7]))
        else:
            for row in rows:
                if row[3] is None:
                    worked = q[4]-row[2]
                    worked_hours = worked.total_seconds() / 3600.0
                    if str(row[2])[8:-9] == str(q[4])[8:-9]:
                        self._cr.execute(
                            "UPDATE hr_attendance SET check_out = " + "'" + str(q[4]) + "'" + ", worked_hours=" + str(worked_hours) + " WHERE employee_id = " + str(q[
                                2]) + " and id =" + str(row[0]) + ";")
                        print("Employee_id :", row[0])
                    else:
                        sqlquery = "INSERT INTO hr_attendance(employee_id,check_in,check_out,worked_hours,create_uid,create_date,write_uid,write_date)values(%s,%s,%s,%s,%s,%s,%s,%s)"
                        self._cr.execute(sqlquery,
                                         (int(str(q[2])), str(q[4]), None, int(0), int(2),
                                          str('2020-07-16 18:27:12'), int(2),
                                          str(datetime.datetime.now())[:-7]))

                else:
                    sqlquery = "INSERT INTO hr_attendance(employee_id,check_in,check_out,worked_hours,create_uid,create_date,write_uid,write_date)values(%s,%s,%s,%s,%s,%s,%s,%s)"
                    self._cr.execute(sqlquery, (int(str(q[2])), str(q[4]), None, int(0), int(2),
                                                str('2020-07-16 18:27:12'), int(2),
                                                str(datetime.datetime.now())[:-7]))
        query = """DELETE FROM mb_uface202_pool"""
        self._cr.execute(query)



class log(models.Model):
    _name = 'mb_uface202.log'
    _description = 'mb_uface202.log'

    name = fields.Many2one('hr.employee', string='Employee')
    uid = fields.Integer()
    os_time = fields.Datetime()
    zk_time = fields.Datetime()
    done = fields.Boolean()


    def write(self):
        print("ok ok ok")


class pool(models.Model):
    _name = 'mb_uface202.pool'
    _description = 'mb_uface202.pool'

    name = fields.Many2one('hr.employee', string='Employee')
    uid = fields.Integer()
    os_time = fields.Datetime()
    zk_time = fields.Datetime()
    done = fields.Boolean()


