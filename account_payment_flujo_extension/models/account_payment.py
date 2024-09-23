from odoo import models, fields

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    mpflujo = fields.Many2one('mp.flujo', string='Flujo')
    mpgrupo_flujo = fields.Many2one('mp.grupo.flujo', string='Grupo de Flujo')

    def action_post(self):
        # Llamamos a la función original para que continúe con el flujo de generación de asiento contable
        res = super(AccountPayment, self).action_post()

        # Iteramos sobre los pagos para heredar los valores de flujo y grupo de flujo a los asientos contables
        for payment in self:
            if payment.move_id:
                # Añadimos los valores del flujo y grupo de flujo al asiento contable generado
                payment.move_id.mp_flujo_id = payment.mp_flujo_id
                payment.move_id.mp_grupo_flujo_id = payment.mp_grupo_flujo_id
                
                # Ahora heredamos los valores de flujo y grupo de flujo también a las líneas del asiento
                for move_line in payment.move_id.line_ids:
                    move_line.mp_flujo_id = payment.mp_flujo_id
                    move_line.mp_grupo_flujo_id = payment.mp_grupo_flujo_id

        return res