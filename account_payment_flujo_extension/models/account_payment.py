from odoo import models, fields

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    mpflujo = fields.Many2one('mp.flujo', string='Flujo')
    mpgrupo_flujo = fields.Many2one('mp.grupo.flujo', string='Grupo de Flujo')

    def post(self):
        # Llamar a la función original de validación
        res = super(AccountPayment, self).post()

        for payment in self:
            # Buscar el asiento contable generado por el pago
            account_move = payment.move_id

            if account_move:
                # Asignar los valores de flujo y grupo de flujo al asiento contable
                account_move.sudo().write({
                    'mp_flujo_id': payment.mp_flujo_id.id,
                    'mp_grupo_flujo_id': payment.mp_grupo_flujo_id.id
                })

                # Asignar también a las líneas del asiento contable
                for line in account_move.line_ids:
                    line.sudo().write({
                        'mp_flujo_id': payment.mp_flujo_id.id,
                        'mp_grupo_flujo_id': payment.mp_grupo_flujo_id.id
                    })

        return res
