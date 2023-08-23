import base64
from odoo import api, exceptions, fields, models, _


class DBPasswordDecryptWizard(models.TransientModel):
    _name = 'db.password.decrypt.wizard'

    encrypt_password = fields.Char("Encrypted Password", required=True)
    preview = fields.Html('Report Preview')

    @api.multi
    def action_password_decryption(self):
        if self.encrypt_password:
            base64_string = self.encrypt_password
            base64_bytes = base64_string.encode("ascii")
            password_string_bytes = base64.b64decode(base64_bytes)
            decrypt_password = password_string_bytes.decode("ascii")
            self.write({'preview': decrypt_password})
        else:
            raise exceptions.ValidationError(_('Please enter password to decrypt!'))
