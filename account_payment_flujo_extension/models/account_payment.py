from odoo import models, fields, api, _
from odoo.exceptions import ValidationError  # Importar ValidationError
import logging

_logger = logging.getLogger(__name__)

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    mp_flujo_id = fields.Many2one('mp.flujo', string='Flujo')
    mp_grupo_flujo_id = fields.Many2one('mp.grupo.flujo', string='Grupo de Flujo')

    @api.model
    def create(self, vals_list):
        """Sobrescribe el método create para asegurarse que Flujo y Grupo de Flujo se asignen correctamente.
        Soporta tanto pagos individuales como múltiples.
        """
        return super(AccountPayment, self).create(vals_list)

    def write(self, vals):
        """Sobrescribe el método write para asegurarse que Flujo y Grupo de Flujo se escriban correctamente"""
        _logger.info("Escribiendo valores de Flujo y Grupo de Flujo: %s", vals)
        return super(AccountPayment, self).write(vals)

    def action_post(self):
        """Sobreescribe el método action_post para asignar los valores de Flujo y Grupo de Flujo a los asientos contables."""
        # Llamada al método original de Odoo para procesar el pago
        res = super(AccountPayment, self).action_post()

        # Asignar los valores de Flujo y Grupo de Flujo a los asientos contables y sus líneas
        for payment in self:
            if payment.move_id:  # Asegúrate de que el asiento contable (move_id) existe
                _logger.info("Asignando Flujo y Grupo de Flujo al asiento contable (account.move) del pago: %s", payment.id)
                payment.move_id.sudo().write({
                    'mp_flujo_id': payment.mp_flujo_id.id,
                    'mp_grupo_flujo_id': payment.mp_grupo_flujo_id.id
                })
                
                # Ahora también asignamos a las líneas del asiento contable (account.move.line)
                for move_line in payment.move_id.line_ids:
                    _logger.info("Asignando Flujo y Grupo de Flujo a las líneas del asiento contable (account.move.line): %s", move_line.id)
                    move_line.sudo().write({
                        'mp_flujo_id': payment.mp_flujo_id.id,
                        'mp_grupo_flujo_id': payment.mp_grupo_flujo_id.id
                    })
            else:
                _logger.warning("No se encontraron asientos contables asociados al pago %s", payment.id)

        return res



_logger = logging.getLogger(__name__)

class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    mp_flujo_id = fields.Many2one(comodel_name="mp.flujo", string="Flujo")
    mp_grupo_flujo_id = fields.Many2one('mp.grupo.flujo', string="Grupo de Flujo")

   
    @api.model
    def default_get(self, fields_list):
        """
        Asegurarnos de que los valores de Flujo y Grupo de Flujo se incluyan cuando se crea el registro del wizard.
        """
        res = super(AccountPaymentRegister, self).default_get(fields_list)
        if 'mp_flujo_id' in self._context:
            res['mp_flujo_id'] = self._context.get('mp_flujo_id')
        if 'mp_grupo_flujo_id' in self._context:
            res['mp_grupo_flujo_id'] = self._context.get('mp_grupo_flujo_id')
        return res

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
        payments = action  # Esto debería ser un conjunto de registros de pagos
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

