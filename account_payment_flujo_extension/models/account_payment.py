from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

# Modelo account.payment
class AccountPayment(models.Model):
    _inherit = 'account.payment'

    mp_flujo_id = fields.Many2one('mp.flujo', string='Flujo')
    mp_grupo_flujo_id = fields.Many2one('mp.grupo.flujo', string='Grupo de Flujo')

    @api.model
    def create(self, vals_list):
        """Sobrescribe el método create para asegurarse que Flujo y Grupo de Flujo se asignen correctamente."""
        _logger.info('Creando pago con valores: %s', vals_list)

        # Asegurarse de que los valores de flujo se están pasando
        if not vals_list.get('mp_flujo_id') and self.env.context.get('default_mp_flujo_id'):
            vals_list['mp_flujo_id'] = self.env.context.get('default_mp_flujo_id')
        if not vals_list.get('mp_grupo_flujo_id') and self.env.context.get('default_mp_grupo_flujo_id'):
            vals_list['mp_grupo_flujo_id'] = self.env.context.get('default_mp_grupo_flujo_id')

        payment = super(AccountPayment, self).create(vals_list)

        # Asignar los valores de Flujo y Grupo de Flujo al asiento contable (account.move)
        if payment.move_id:
            _logger.info('Asignando Flujo y Grupo de Flujo al asiento contable (account.move) del pago %s', payment.id)
            payment.move_id.sudo().write({
                'mp_flujo_id': payment.mp_flujo_id.id,
                'mp_grupo_flujo_id': payment.mp_grupo_flujo_id.id
            })

            # Asignar a las líneas del asiento contable
            for line in payment.move_id.line_ids:
                line.sudo().write({
                    'mp_flujo_id': payment.mp_flujo_id.id,
                    'mp_grupo_flujo_id': payment.mp_grupo_flujo_id.id
                })

        return payment

    def write(self, vals):
        """Sobreescribe el método write para asegurarse que Flujo y Grupo de Flujo se escriban correctamente."""
        _logger.info("Escribiendo valores de Flujo y Grupo de Flujo: %s", vals)
        return super(AccountPayment, self).write(vals)

    def action_post(self):
        """Sobreescribe el método action_post para asignar los valores de Flujo y Grupo de Flujo a los asientos contables."""
        res = super(AccountPayment, self).action_post()

        for payment in self:
            if payment.move_id:  # Verificamos si existe el asiento contable (move_id)
                _logger.info("Asignando Flujo y Grupo de Flujo al asiento contable (account.move) del pago: %s", payment.id)
                payment.move_id.sudo().write({
                    'mp_flujo_id': payment.mp_flujo_id.id,
                    'mp_grupo_flujo_id': payment.mp_grupo_flujo_id.id
                })

                # Asignar también a las líneas del asiento contable
                for move_line in payment.move_id.line_ids:
                    _logger.info("Asignando Flujo y Grupo de Flujo a las líneas del asiento contable (account.move.line): %s", move_line.id)
                    move_line.sudo().write({
                        'mp_flujo_id': payment.mp_flujo_id.id,
                        'mp_grupo_flujo_id': payment.mp_grupo_flujo_id.id
                    })
            else:
                _logger.warning("No se encontraron asientos contables asociados al pago %s", payment.id)

        return res


# Wizard account.payment.register
class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    mp_flujo_id = fields.Many2one(comodel_name="mp.flujo", string="Flujo", required=True)
    mp_grupo_flujo_id = fields.Many2one('mp.grupo.flujo', string="Grupo de Flujo", required=True)

    @api.model
    def default_get(self, fields_list):
        """Asegurarnos de que los valores de Flujo y Grupo de Flujo se incluyan cuando se crea el registro del wizard."""
        res = super(AccountPaymentRegister, self).default_get(fields_list)
        if 'mp_flujo_id' in self._context:
            res['mp_flujo_id'] = self._context.get('mp_flujo_id')
        if 'mp_grupo_flujo_id' in self._context:
            res['mp_grupo_flujo_id'] = self._context.get('mp_grupo_flujo_id')
        return res

    def _create_payment_vals_from_wizard(self, batch_result):
        """
        Sobrescribe la función para asegurarse de que Flujo y Grupo de Flujo se asignen correctamente al crear los pagos.
        """
        payment_vals = super(AccountPaymentRegister, self)._create_payment_vals_from_wizard(batch_result)
        payment_vals.update({
            'mp_flujo_id': self.mp_flujo_id.id,
            'mp_grupo_flujo_id': self.mp_grupo_flujo_id.id,
        })
        return payment_vals

    def action_create_payments(self):
        """
        Heredamos la función action_create_payments para asegurarnos de que los valores de Flujo y Grupo de Flujo
        se asignen correctamente tanto al pago como al asiento contable después de que los pagos han sido creados.
        """
        # Llamamos al método original para crear los pagos
        action = super(AccountPaymentRegister, self).action_create_payments()

        # Comprobamos si el resultado es una acción (dict) o un conjunto de registros
        if isinstance(action, dict):
            # Si es una acción, devolvemos la acción inmediatamente (sin cambios)
            return action

        # Si se trata de registros de pagos, iteramos y asignamos los valores
        payments = action
        for payment in payments:
            # Asignar Flujo y Grupo de Flujo al pago
            payment.write({
                'mp_flujo_id': self.mp_flujo_id.id,
                'mp_grupo_flujo_id': self.mp_grupo_flujo_id.id,
            })
            _logger.info("Asignando Flujo %s y Grupo de Flujo %s al pago %s", self.mp_flujo_id.name, self.mp_grupo_flujo_id.name, payment.id)

            # Verificamos si el asiento contable (move_id) existe
            if payment.move_id:
                move = payment.move_id

                # Asignamos los valores al asiento en borrador
                if move.state == 'draft':
                    move.write({
                        'mp_flujo_id': payment.mp_flujo_id.id,
                        'mp_grupo_flujo_id': payment.mp_grupo_flujo_id.id
                    })
                    _logger.info("Asignando Flujo y Grupo de Flujo al asiento contable (account.move) %s", move.id)

                    # Asignamos los valores a las líneas del asiento contable (account.move.line)
                    for move_line in move.line_ids:
                        move_line.write({
                            'mp_flujo_id': payment.mp_flujo_id.id,
                            'mp_grupo_flujo_id': payment.mp_grupo_flujo_id.id
                        })
                else:
                    _logger.info("El asiento %s ya está validado, no se puede modificar.", move.name)
            else:
                _logger.warning("No se encontraron asientos contables asociados al pago %s", payment.id)

        return action
