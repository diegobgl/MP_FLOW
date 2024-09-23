from odoo import models, fields

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    mpflujo = fields.Many2one('mp.flujo', string='Flujo')
    mpgrupo_flujo = fields.Many2one('mp.grupo.flujo', string='Grupo de Flujo')

    def action_post(self):
        # First, execute the standard method to create the payment and journal entry
        res = super(AccountPayment, self).action_post()

        # Loop through the payments to find the related journal entries
        for payment in self:
            # Get the related journal entries (account.move)
            account_move = payment.move_id  # Assuming `move_id` links to the journal entry

            if account_move:
                # Assign the "Flujo" and "Grupo de Flujo" from the payment to the journal entry
                account_move.write({
                    'mp_flujo_id': payment.mp_flujo_id.id,
                    'mp_grupo_flujo_id': payment.mp_grupo_flujo_id.id,
                })

                # Assign the "Flujo" and "Grupo de Flujo" to the lines of the journal entry
                for line in account_move.line_ids:
                    line.write({
                        'mp_flujo_id': payment.mp_flujo_id.id,
                        'mp_grupo_flujo_id': payment.mp_grupo_flujo_id.id,
                    })

        return res

