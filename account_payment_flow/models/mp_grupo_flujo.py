from odoo import models, fields, api

class MpGrupoFlujo(models.Model):
    _name = 'mp.grupo.flujo'
    _rec_name = "nombre"

    nombre = fields.Char(string="Nombre")

    # Relación simplificada para conectar con los flujos
    flujo_ids = fields.Many2many(
        comodel_name="mp.flujo",
        relation="mp_flujo_grupo_rel",  # Reutilizar la misma relación
        column1="grupo_flujo_id",
        column2="flujo_id",
        string="Flujos"
    )
