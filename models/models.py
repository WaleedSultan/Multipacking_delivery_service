# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools.float_utils import float_compare

class multipack(models.Model):
    _inherit = 'stock.picking'
    single_pack = fields.Boolean(default = True)
    multipack = fields.Boolean(default = False)

    @api.onchange('multipack','single_pack')
    def multipack_change(self):
        if self.multipack == True:
            self.single_pack = False
        if self.multipack == False:
            self.single_pack=True

class ChooseDeliveryPackage(models.TransientModel):
    _inherit = "choose.delivery.package"

    domain_ids = fields.Many2many('product.product',"testing_table")
    product_id = fields.Many2many('product.product',domain="[('id', 'in', domain_ids)]")

    @api.onchange('delivery_packaging_id')
    def _test_compute(self):
        id_list = []
        for line in self.picking_id.move_line_ids:
            id_list.append(line.product_id.id)
        if len(id_list):
            self.domain_ids = id_list
        else:
            self.domain_ids =False


    def action_put_in_pack(self):
        picking_move_lines = self.picking_id.move_line_ids
        if not self.picking_id.picking_type_id.show_reserved and not self.env.context.get('barcode_view'):
            picking_move_lines = self.picking_id.move_line_nosuggest_ids

        move_line_ids = picking_move_lines.filtered(lambda ml:
            float_compare(ml.qty_done, 0.0, precision_rounding=ml.product_uom_id.rounding) > 0
            and not ml.result_package_id
        )
        if self.picking_id.single_pack:
            if not move_line_ids:
                move_line_ids = picking_move_lines.filtered(lambda ml: float_compare(ml.product_uom_qty, 0.0,
                                     precision_rounding=ml.product_uom_id.rounding) > 0 and float_compare(ml.qty_done, 0.0,
                                     precision_rounding=ml.product_uom_id.rounding) == 0)
        else:
            move_id  = []
            for line in self.picking_id.move_line_ids:
                if line.product_id in self.product_id:
                    move_id.append(line.id)
            move_line_ids  = self.env['stock.move.line'].search([ ('id', 'in', move_id)])

        # if move_id == []:
        #     pass



        delivery_package = self.picking_id._put_in_pack(move_line_ids)
        # write shipping weight and product_packaging on 'stock_quant_package' if needed
        if self.delivery_packaging_id:
            delivery_package.packaging_id = self.delivery_packaging_id
        if self.shipping_weight:
            delivery_package.shipping_weight = self.shipping_weight








