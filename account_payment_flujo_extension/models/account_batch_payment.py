from odoo import models, fields

class AccountBatchPayment(models.Model):
    _inherit = 'account.batch.payment'

    mpflujo = fields.Many2one('mp.flujo', string='Flujo')
    mpgrupo_flujo = fields.Many2one('mp.grupo.flujo', string='Grupo de Flujo')
