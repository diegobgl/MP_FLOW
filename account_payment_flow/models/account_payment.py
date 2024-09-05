
from odoo import models, fields

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    # Fields and methods adjustments for Odoo 17
    flow_reference = fields.Char(string='Flow Reference')
