from odoo import fields, models


class MpFlujo(models.Model):
    _name = 'mp.flujo'
    _rec_name = "display_name"

    codigo = fields.Char()
    grupo_flujo_ids = fields.Many2many(comodel_name="mp.grupo.flujo", relation="mp_flujo_grupo_rel", column1="flujo_id",
                                       column2="grupo_flujo_id")
    decripcion = fields.Text()
    display_name = fields.Text(compute="_compute_display_name")
    mp_grupo_flujo_id = fields.Many2one(comodel_name="mp.grupo.flujo")

    def _compute_display_name(self):
        for flujo_id in self:
            flujo_id.display_name = str(flujo_id.codigo) + str(": ") + str(flujo_id.decripcion)
