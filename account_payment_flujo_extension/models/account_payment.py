from odoo import models, fields

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    mpflujo = fields.Many2one('mp.flujo', string='Flujo')
    mpgrupo_flujo = fields.Many2one('mp.grupo.flujo', string='Grupo de Flujo')

    def action_post(self):
        # Llamamos a la función original para validar el pago
        res = super(AccountPayment, self).action_post()

        # Recorremos los pagos y obtenemos los asientos generados
        for payment in self:
            if payment.move_id:
                # Asignar los valores de Flujo y Grupo de Flujo al asiento contable
                payment.move_id.mp_flujo_id = payment.mp_flujo_id
                payment.move_id.mp_grupo_flujo_id = payment.mp_grupo_flujo_id

                # Asignar los valores de Flujo y Grupo de Flujo a cada línea del asiento
                for line in payment.move_id.line_ids:
                    line.mp_flujo_id = payment.mp_flujo_id
                    line.mp_grupo_flujo_id = payment.mp_grupo_flujo_id

        return res
