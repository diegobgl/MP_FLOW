
from odoo import models, fields

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    # Custom fields and methods adjustments for Odoo 17
    payment_date = fields.Date(string='Payment Date')
