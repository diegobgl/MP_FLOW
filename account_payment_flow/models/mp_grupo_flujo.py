from odoo import fields, models


class MpGrupoFlujo(models.Model):
    _name = 'mp.grupo.flujo'
    _rec_name = "nombre"

    nombre = fields.Char()
    flujo_id = fields.Many2one(comodel_name="mp.flujo")

    mp_flujo_ids = fields.One2many(comodel_name="mp.flujo", inverse_name="mp_grupo_flujo_id",
                                   compute="_compute_mp_flujo_ids")

    def _compute_mp_flujo_ids(self):
        for grupo_id in self:
            flujo_ids = self.env["mp.flujo"].search([("grupo_flujo_ids", "=", grupo_id.id)])
            for flujo_id in flujo_ids:
                grupo_id.mp_flujo_ids += flujo_id
