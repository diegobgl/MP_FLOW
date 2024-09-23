from odoo import models, fields

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    mpflujo = fields.Many2one('mp.flujo', string='Flujo')
    mpgrupo_flujo = fields.Many2one('mp.grupo.flujo', string='Grupo de Flujo')

    def _create_payment_entry(self, amount):
        # Call the super method to create the journal entry
        move = super(AccountPayment, self)._create_payment_entry(amount)
        
        # Assign the 'Flujo' and 'Grupo de Flujo' from the payment to the account.move
        if self.mp_flujo_id or self.mp_grupo_flujo_id:
            move.write({
                'mp_flujo_id': self.mp_flujo_id.id,
                'mp_grupo_flujo_id': self.mp_grupo_flujo_id.id,
            })

        # Assign the 'Flujo' and 'Grupo de Flujo' to the lines of the journal entry
        for line in move.line_ids:
            line.write({
                'mp_flujo_id': self.mp_flujo_id.id,
                'mp_grupo_flujo_id': self.mp_grupo_flujo_id.id,
            })

        return move

