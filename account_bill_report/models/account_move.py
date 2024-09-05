
from odoo import models, fields

class AccountMove(models.Model):
    _inherit = 'account.move'

    # Custom fields and methods adjustments for Odoo 17
    bill_date = fields.Date(string='Bill Date')
