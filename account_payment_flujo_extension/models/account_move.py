from odoo import models, fields
import logging


_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    mp_flujo_id = fields.Many2one('mp.flujo', string="Flujo")
    mp_grupo_flujo_id = fields.Many2one('mp.grupo.flujo', string="Grupo de Flujo")


    def action_post(self):
        """Overriding action_post to pass mp_flujo_id and mp_grupo_flujo_id to the account move and its lines."""
        _logger.info("Ejecutando action_post para el pago con ID: %s", self.id)

        # Verificar que los campos mp_flujo_id y mp_grupo_flujo_id están presentes en el modelo account.payment
        if not self.mp_flujo_id or not self.mp_grupo_flujo_id:
            _logger.warning("Los valores de Flujo o Grupo de Flujo no están asignados en el pago con ID: %s", self.id)
        
        # Ejecutar la función original para crear el asiento contable
        super(AccountPayment, self).action_post()

        # Asignar los valores de mp_flujo_id y mp_grupo_flujo_id al asiento contable (account.move)
        account_move = self.move_id.sudo()
        account_move.write({
            'mp_flujo_id': self.mp_flujo_id.id,
            'mp_grupo_flujo_id': self.mp_grupo_flujo_id.id,
        })

        _logger.info("Valores escritos en el asiento contable: Flujo ID: %s, Grupo de Flujo ID: %s", 
                     account_move.mp_flujo_id.id, account_move.mp_grupo_flujo_id.id)

        # Asignar los valores de mp_flujo_id y mp_grupo_flujo_id a las líneas del asiento contable (account.move.line)
        for line in account_move.line_ids:
            line.write({
                'mp_flujo_id': self.mp_flujo_id.id,
                'mp_grupo_flujo_id': self.mp_grupo_flujo_id.id,
            })
            _logger.info("Valores escritos en la línea del asiento: Flujo ID: %s, Grupo de Flujo ID: %s", 
                         line.mp_flujo_id.id, line.mp_grupo_flujo_id.id)

        return True


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    mp_flujo_id = fields.Many2one(related='move_id.mp_flujo_id', store=True, string="Flujo")
    mp_grupo_flujo_id = fields.Many2one(related='move_id.mp_grupo_flujo_id', store=True, string="Grupo de Flujo")


