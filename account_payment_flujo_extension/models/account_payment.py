from odoo import models, fields
import logging

_logger = logging.getLogger(__name__)

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    mp_flujo_id = fields.Many2one('mp.flujo', string='Flujo')
    mp_grupo_flujo_id = fields.Many2one('mp.grupo.flujo', string='Grupo de Flujo')

    def create(self, vals):
        # Validar que los valores de Flujo y Grupo de Flujo están presentes
        if not vals.get('mp_flujo_id') or not vals.get('mp_grupo_flujo_id'):
            raise ValidationError("Es necesario asignar el Flujo y Grupo de Flujo antes de continuar.")
        return super(AccountPayment, self).create(vals)

    def write(self, vals):
        # Log para verificar la escritura de valores
        _logger.info("Escribiendo valores de Flujo y Grupo de Flujo antes de validar")
        return super(AccountPayment, self).write(vals)

    def action_post(self):
        _logger.info("Ejecutando action_post para el pago con ID: %s", self.id)

        # Validación de que los valores de flujo y grupo de flujo están presentes
        if not self.mp_flujo_id or not self.mp_grupo_flujo_id:
            _logger.warning("Los valores de Flujo o Grupo de Flujo no están asignados en el pago con ID: %s", self.id)

        # Lógica principal del asiento
        res = super(AccountPayment, self).action_post()

        if self.move_id:
            # Asignación de los valores al asiento creado
            account_move = self.move_id.sudo()
            _logger.info("Asignando Flujo y Grupo de Flujo al asiento contable: %s", account_move.id)
            account_move.write({
                'mp_flujo_id': self.mp_flujo_id.id,
                'mp_grupo_flujo_id': self.mp_grupo_flujo_id.id,
            })

            # Asignación de los valores a las líneas del asiento
            for line in account_move.line_ids:
                _logger.info("Asignando Flujo y Grupo de Flujo a las líneas del asiento: %s", line.id)
                line.sudo().write({
                    'mp_flujo_id': self.mp_flujo_id.id,
                    'mp_grupo_flujo_id': self.mp_grupo_flujo_id.id,
                })
        else:
            _logger.warning("No se encontró ningún asiento relacionado con el pago ID: %s", self.id)

        return res
