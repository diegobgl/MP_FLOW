from odoo import models, fields
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    mp_flujo_id = fields.Many2one('mp.flujo', string="Flujo")
    mp_grupo_flujo_id = fields.Many2one('mp.grupo.flujo', string="Grupo de Flujo")

    def action_post(self):
        # Llamada al método original
        res = super(AccountMove, self).action_post()

        # Lógica adicional para pasar los valores de flujo y grupo de flujo desde el pago
        for move in self:
            if move.payment_id:
                if move.payment_id.mp_flujo_id and move.payment_id.mp_grupo_flujo_id:
                    _logger.info("Asignando Flujo y Grupo de Flujo al asiento: %s", move.id)
                    move.sudo().write({
                        'mp_flujo_id': move.payment_id.mp_flujo_id.id,
                        'mp_grupo_flujo_id': move.payment_id.mp_grupo_flujo_id.id
                    })
                    for line in move.line_ids:
                        _logger.info("Asignando Flujo y Grupo de Flujo a las líneas del asiento: %s", line.id)
                        line.sudo().write({
                            'mp_flujo_id': move.payment_id.mp_flujo_id.id,
                            'mp_grupo_flujo_id': move.payment_id.mp_grupo_flujo_id.id
                        })
                else:
                    _logger.warning("No se encontraron valores de Flujo o Grupo de Flujo en el pago %s", move.payment_id.id)
        return res

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    mp_flujo_id = fields.Many2one(related='move_id.mp_flujo_id', store=True, string="Flujo")
    mp_grupo_flujo_id = fields.Many2one(related='move_id.mp_grupo_flujo_id', store=True, string="Grupo de Flujo")
