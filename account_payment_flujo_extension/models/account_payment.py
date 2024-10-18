from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

# Modelo account.payment
class AccountPayment(models.Model):
    _inherit = 'account.payment'

    mp_flujo_ids = fields.Many2many('mp.flujo', string='Flujos')
    mp_grupo_flujo_id = fields.Many2one('mp.grupo.flujo', string='Grupo de Flujo')
    partner_vat = fields.Char(
        string='VAT',
        related='partner_id.vat',
        readonly=True,
        store=True
    )

    @api.model
    def create(self, vals):
        """
        Sobrescribe el método create para asegurarse de que Flujo y Grupo de Flujo se asignen correctamente.
        """
        _logger.info('Creando pago con valores: %s', vals)

        # Asignar valores de Flujo y Grupo de Flujo si están en el contexto y no en los vals
        if 'mp_flujo_id' not in vals and self.env.context.get('default_mp_flujo_id'):
            vals['mp_flujo_id'] = self.env.context.get('default_mp_flujo_id')
        if 'mp_grupo_flujo_id' not in vals and self.env.context.get('default_mp_grupo_flujo_id'):
            vals['mp_grupo_flujo_id'] = self.env.context.get('default_mp_grupo_flujo_id')

        # Crear el pago
        payment = super(AccountPayment, self).create(vals)

        # Asignar valores al asiento contable si existe
        if payment.move_id:
            _logger.info('Asignando Flujo y Grupo de Flujo al asiento contable (account.move) del pago %s', payment.id)
            payment.move_id.sudo().write({
                'mp_flujo_id': payment.mp_flujo_id.id,
                'mp_grupo_flujo_id': payment.mp_grupo_flujo_id.id
            })

            # Asignar valores a las líneas del asiento contable
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
        res = super(AccountPayment, self).action_post()

        for payment in self:
            if payment.move_id:  # Asegúrate de que el asiento contable (move_id) existe
                _logger.info("Asignando Flujos y Grupo de Flujo al asiento contable (account.move) del pago: %s", payment.id)
                payment.move_id.sudo().write({
                    'mp_flujo_ids': [(6, 0, payment.mp_flujo_ids.ids)],
                    'mp_grupo_flujo_id': payment.mp_grupo_flujo_id.id
                })

                # Asignar también a las líneas del asiento contable
                for move_line in payment.move_id.line_ids:
                    _logger.info("Asignando Flujos y Grupo de Flujo a las líneas del asiento contable (account.move.line): %s", move_line.id)
                    move_line.sudo().write({
                        'mp_flujo_ids': [(6, 0, payment.mp_flujo_ids.ids)],
                        'mp_grupo_flujo_id': payment.mp_grupo_flujo_id.id
                    })
            else:
                _logger.warning("No se encontraron asientos contables asociados al pago %s", payment.id)

        return res



# Wizard account.payment.register
class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    mp_flujo_ids = fields.Many2many(comodel_name="mp.flujo", string="Flujos", required=True)
    mp_grupo_flujo_id = fields.Many2one('mp.grupo.flujo', string="Grupo de Flujo", required=True)

    def action_create_payments(self):
        """
        Heredamos la función action_create_payments para asegurarnos de que los valores de Flujo y Grupo de Flujo
        se asignen correctamente tanto al pago como al asiento contable después de que los pagos han sido creados.
        """
        # Actualizar el contexto con los valores de Flujo y Grupo de Flujo
        ctx = dict(self.env.context)
        ctx.update({
            'default_mp_flujo_ids': self.mp_flujo_ids.ids,
            'default_mp_grupo_flujo_id': self.mp_grupo_flujo_id.id,
        })

        # Llamamos al método original con el nuevo contexto
        payments = super(AccountPaymentRegister, self.with_context(ctx)).action_create_payments()

        return payments
