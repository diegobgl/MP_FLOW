from odoo import models, fields, api

class MpFlujo(models.Model):
    _name = 'mp.flujo'
    _rec_name = "display_name"

    codigo = fields.Char(string="Código")
    descripcion = fields.Text(string="Descripción")  
    # Define la relación Many2many simplificada
    grupo_flujo_id = fields.Many2one(
        comodel_name="mp.grupo.flujo",
        string="Grupo de Flujo"
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
