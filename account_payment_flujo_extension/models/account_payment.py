from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

# Modelo account.payment
class AccountPayment(models.Model):
    _inherit = 'account.payment'

    mp_flujo_id = fields.Many2one('mp.flujo', string='Flujo')
    mp_grupo_flujo_id = fields.Many2one('mp.grupo.flujo', string='Grupo de Flujo')

    @api.model
    def create(self, vals):
        """
        Sobrescribe el método create para asegurarse de que Flujo y Grupo de Flujo se asignen correctamente.
        """
        # Si los valores de flujo y grupo de flujo están en el contexto, los asignamos a los vals
        if 'mp_flujo_id' not in vals and self.env.context.get('default_mp_flujo_id'):
            vals['mp_flujo_id'] = self.env.context.get('default_mp_flujo_id')
        if 'mp_grupo_flujo_id' not in vals and self.env.context.get('default_mp_grupo_flujo_id'):
            vals['mp_grupo_flujo_id'] = self.env.context.get('default_mp_grupo_flujo_id')

        # Crear el pago
        payment = super(AccountPayment, self).create(vals)

        # Asignar los valores de Flujo y Grupo de Flujo al asiento contable si existe
        if payment.move_id:
            payment.move_id.sudo().write({
                'mp_flujo_id': payment.mp_flujo_id.id,
                'mp_grupo_flujo_id': payment.mp_grupo_flujo_id.id
            })

            # Asignar los valores a las líneas del asiento contable también
            for line in payment.move_id.line_ids:
                line.sudo().write({
                    'mp_flujo_id': payment.mp_flujo_id.id,
                    'mp_grupo_flujo_id': payment.mp_grupo_flujo_id.id
                })

        return payment

    def action_post(self):
        """
        Sobreescribe el método action_post para asignar los valores de Flujo y Grupo de Flujo a los asientos contables.
        """
        # Llamar al método original de Odoo para procesar el pago
        res = super(AccountPayment, self).action_post()

        for payment in self:
            if payment.move_id:  # Si el asiento contable existe
                payment.move_id.sudo().write({
                    'mp_flujo_id': payment.mp_flujo_id.id,
                    'mp_grupo_flujo_id': payment.mp_grupo_flujo_id.id
                })

                # Asignar los valores a las líneas del asiento contable también
                for move_line in payment.move_id.line_ids:
                    move_line.sudo().write({
                        'mp_flujo_id': payment.mp_flujo_id.id,
                        'mp_grupo_flujo_id': payment.mp_grupo_flujo_id.id
                    })
        return res


# Wizard account.payment.register
class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    mp_flujo_id = fields.Many2many(comodel_name="mp.flujo", string="Flujos", required=True)
    mp_grupo_flujo_id = fields.Many2one('mp.grupo.flujo', string="Grupo de Flujo", required=True)

    def action_create_payments(self):
        # Actualizar el contexto con los valores de Flujo y Grupo de Flujo
        ctx = dict(self.env.context)
        ctx.update({
            'default_mp_flujo_id': self.mp_flujo_id.id,
            'default_mp_grupo_flujo_id': self.mp_grupo_flujo_id.id,
        })

        # Llamar al método original con el nuevo contexto
        payments = super(AccountPaymentRegister, self.with_context(ctx)).action_create_payments()

        return payments
