import os
import pyminizip
import base64
import re
from datetime import date
from cryptography.fernet import Fernet
from odoo import models, fields, api, tools, _
from odoo.exceptions import ValidationError


class DB_Backup(models.Model):
    _inherit = 'db.backup'

    user_ids = fields.Many2many('res.users', 'db_backup_users_rel', string="Notifiers",
                                help="List of users who get notification after db backup")
    mail_from = fields.Char(string="E-mail(from)", required=True, track_visibility="onchange")

    @api.onchange('mail_from')
    def onchange_mail_from(self):
        if self.mail_from:
            match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$',
                             self.mail_from)
            if match == None:
                raise ValidationError('Not a valid E-mail ID')

    @api.model
    def schedule_backup(self):
        res = super(DB_Backup, self).schedule_backup()
        # password code
        conf_ids = self.search([])
        if conf_ids:
            file_path = conf_ids[0].folder
            for db_file in sorted(os.listdir(file_path)):
                if db_file[0:10] == date.today().strftime("%Y_%m_%d"):
                    key = Fernet.generate_key()
                    sample_string_bytes = key.decode("utf-8").encode("ascii")
                    base64_bytes = base64.b64encode(sample_string_bytes)
                    en_password = base64_bytes.decode("ascii")
                    full_path = file_path + '/' + db_file
                    pyminizip.compress(full_path, '/'+db_file[0:-4] + '_backup',
                                       full_path[0:-4] + '_backup.zip',
                                       key,
                                       0)
                    os.remove(full_path)
                    receiver_users = conf_ids[-1].user_ids
                    mail_from = conf_ids[-1].mail_from
                    self.action_mail_send(receiver_users, mail_from, en_password, db_file[0:-4])
        return res

    @api.multi
    def action_mail_send(self, receiver_users, mail_from, en_password, db_name):
        to_receiver_receipt_list = [i.partner_id.email for i in receiver_users]
        to_receiver = ';'.join(map(lambda x: x, to_receiver_receipt_list))
        if to_receiver_receipt_list and to_receiver and mail_from:
            body = '<p><strong>Dear Concern,</strong></p> ' \
                   '<p>' + 'Here is the password <strong>"' \
                   + en_password + '"</strong>' \
                   + ' for the database, ' + db_name + '</p>' \
                '<p>NB.This password is encrypted. </p>'\
                '<p><i>**Please do not reply this mail.</i></p>'\
                '<p>BJIT ERP</p>'
            mail_values = {
                'subject': 'Backup database password',
                'body_html': body,
                'email_to': to_receiver,
                'email_from': mail_from,
            }
            create_and_send_email = self.env['mail.mail'].create(mail_values)
            create_and_send_email.send()
