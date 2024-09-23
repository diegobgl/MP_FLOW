from odoo import models, fields

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    mpflujo = fields.Many2one('mp.flujo', string='Flujo')
    mpgrupo_flujo = fields.Many2one('mp.grupo.flujo', string='Grupo de Flujo')

    @api.model
    def _create_payment_entry(self, amount):
        # Llamada al super para generar el asiento contable
        move = super(AccountPayment, self)._create_payment_entry(amount)
        
        # Asignar los valores de flujo y grupo de flujo al asiento contable
        move.mp_flujo_id = self.mp_flujo_id
        move.mp_grupo_flujo_id = self.mp_grupo_flujo_id
        
        # Asignar también a las líneas del asiento si es necesario
        for line in move.line_ids:
            line.mp_flujo_id = self.mp_flujo_id
            line.mp_grupo_flujo_id = self.mp_grupo_flujo_id

        return move