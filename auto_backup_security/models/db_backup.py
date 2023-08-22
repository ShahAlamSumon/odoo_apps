import os
from datetime import date
from cryptography.fernet import Fernet
import pyminizip
import base64
from odoo import models, fields, api, tools, _


class DB_Backup(models.Model):
    _inherit = 'db.backup'

    user_ids = fields.Many2many('res.users', 'db_backup_users_rel', string="Notifiers",
                                help="List of users who get notification after db backup")

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
                    receiver_users = conf_ids[0].user_ids
                    self.action_mail_send(receiver_users, en_password, db_file[0:-4])
        return res

    @api.multi
    def action_mail_send(self, receiver_users, en_password, db_name):
        to_receiver_receipt_list = [i.partner_id.email for i in receiver_users]
        to_receiver = ';'.join(map(lambda x: x, to_receiver_receipt_list))
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
            'email_from': 'erp_bjit@bjitgroup.com',
        }
        create_and_send_email = self.env['mail.mail'].create(mail_values)
        create_and_send_email.send()
