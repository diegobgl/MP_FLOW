from odoo import models, fields
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    # Cambiamos mp_flujo_ids a mp_flujo_id, ya que la relación es Many2one
    mp_flujo_id = fields.Many2one(
        'mp.flujo', string="Flujo"
    )
    mp_grupo_flujo_id = fields.Many2one(
        'mp.grupo.flujo', string="Grupo de Flujo"
    )
    
    partner_vat = fields.Char(
        string='VAT',
        related='partner_id.vat',
        readonly=True,
        store=True  # Almacenar para que sea más eficiente en vistas tree
    )

    def action_post(self):
        # Llamada al método original
        res = super(AccountMove, self).action_post()

        for move in self:
            if move.payment_id:
                # Si el pago tiene valores de flujo y grupo de flujo asignados
                if move.payment_id.mp_flujo_id and move.payment_id.mp_grupo_flujo_id:
                    move.sudo().write({
                        'mp_flujo_id': move.payment_id.mp_flujo_id.id,
                        'mp_grupo_flujo_id': move.payment_id.mp_grupo_flujo_id.id
                    })

                    # Asignar estos valores a las líneas del asiento también
                    for line in move.line_ids:
                        line.sudo().write({
                            'mp_flujo_id': move.payment_id.mp_flujo_id.id,
                            'mp_grupo_flujo_id': move.payment_id.mp_grupo_flujo_id.id
                        })
        return res


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    # Cambiamos mp_flujo_ids a mp_flujo_id, ya que la relación es Many2one
    mp_flujo_id = fields.Many2one(
        related='move_id.mp_flujo_id', store=True, string="Flujo"
    )
    mp_grupo_flujo_id = fields.Many2one(
        related='move_id.mp_grupo_flujo_id', store=True, string="Grupo de Flujo"
    )
