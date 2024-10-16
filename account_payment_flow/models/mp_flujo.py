from odoo import models, fields, api

class MpFlujo(models.Model):
    _name = 'mp.flujo'
    _rec_name = "display_name"

    codigo = fields.Char(string="Código")
    descripcion = fields.Text(string="Descripción")
    # Define la relación Many2many simplificada
    grupo_flujo_ids = fields.Many2many(
        comodel_name="mp.grupo.flujo",
        relation="mp_flujo_grupo_rel",  # Nombre de relación único
        column1="flujo_id",
        column2="grupo_flujo_id",
        string="Grupos de Flujo"
    )
    display_name = fields.Char(
        compute="_compute_display_name", 
        string="Nombre de Visualización", 
        store=True
    )

    @api.depends('codigo', 'descripcion')
    def _compute_display_name(self):
        for flujo in self:
            flujo.display_name = f"{flujo.codigo or ''}: {flujo.descripcion or ''}"
