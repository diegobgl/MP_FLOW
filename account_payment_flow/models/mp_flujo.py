from odoo import models, fields, api

class MpFlujo(models.Model):
    _name = 'mp.flujo'
    _rec_name = "display_name"

    codigo = fields.Char(string="Código")
    
    # Define el Many2many con un nombre de relación único para evitar conflictos
    grupo_flujo_ids = fields.Many2many(
        comodel_name="mp.grupo.flujo",
        relation="mp_flujo_grupo_rel",  # Nombre único de la relación
        column1="flujo_id",
        column2="grupo_flujo_id",
        string="Grupos de Flujo"
    )

    decripcion = fields.Text(string="Descripción")
    
    # Campo calculado para mostrar un nombre de visualización
    display_name = fields.Char(
        compute="_compute_display_name", 
        string="Nombre de Visualización", 
        store=True
    )
    
    # Relación Many2one con mp.grupo.flujo
    mp_grupo_flujo_id = fields.Many2one(
        comodel_name="mp.grupo.flujo", 
        string="Grupo de Flujo"
    )

    @api.depends('codigo', 'decripcion')
    def _compute_display_name(self):
        """ Compute method to set the display name based on codigo and descripcion. """
        for flujo in self:
            # Ensure both fields are not None to avoid formatting issues
            codigo = flujo.codigo or ''
            descripcion = flujo.decripcion or ''
            flujo.display_name = f"{codigo}: {descripcion}"
