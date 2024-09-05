from odoo import models, fields, api

class MpFlujo(models.Model):
    _name = 'mp.flujo'
    _rec_name = "display_name"

    codigo = fields.Char(string="Código")
    
    # Define el Many2many con un nombre de relación único
    grupo_flujo_ids = fields.Many2many(
        comodel_name="mp.grupo.flujo",
        relation="mp_flujo_grupo_rel",  # Nombre de relación único
        column1="flujo_id",
        column2="grupo_flujo_id",
        string="Grupos de Flujo"
    )

    decripcion = fields.Text(string="Descripción")
    display_name = fields.Char(
        compute="_compute_display_name", 
        string="Nombre de Visualización", 
        store=True
    )
    
    mp_grupo_flujo_id = fields.Many2one(
        comodel_name="mp.grupo.flujo", 
        string="Grupo de Flujo"
    )

    @api.depends('codigo', 'decripcion')
    def _compute_display_name(self):
        for flujo in self:
            flujo.display_name = f"{flujo.codigo or ''}: {flujo.decripcion or ''}"
