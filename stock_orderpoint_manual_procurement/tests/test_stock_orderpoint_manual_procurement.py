# -*- coding: utf-8 -*-
# Copyright 2016 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp.tests import common


class TestStockWarehouseOrderpoint(common.TransactionCase):

    def setUp(self):
        super(TestStockWarehouseOrderpoint, self).setUp()

        # Get required Model
        self.reordering_rule_model = self.env['stock.warehouse.orderpoint']
        self.product_model = self.env['product.product']
        self.product_ctg_model = self.env['product.category']
        self.stock_change_model = self.env['stock.change.product.qty']
        self.make_procurement_orderpoint_model =\
            self.env['make.procurement.orderpoint']

        # Get required Model data
        self.product_uom = self.env.ref('product.product_uom_unit')
        self.location = self.env.ref('stock.stock_location_stock')
        self.product = self.env.ref('product.product_product_7')

        # Create Product category and Product
        self.product_ctg = self._create_product_category()
        self.product = self._create_product()

        # Add default quantity
        quantity = 20.00
        self._update_product_qty(self.product, self.location, quantity)

        # Create Reordering Rule
        self.create_orderpoint()

    def _create_product_category(self):
        """Create a Product Category."""
        product_ctg = self.product_ctg_model.create({
            'name': 'test_product_ctg',
            'type': 'normal',
        })
        return product_ctg

    def _create_product(self):
        """Create a Product."""
        product = self.product_model.create({
            'name': 'Test Product',
            'categ_id': self.product_ctg.id,
            'type': 'product',
            'uom_id': self.product_uom.id,
        })
        return product

    def _update_product_qty(self, product, location, quantity):
        """Update Product quantity."""
        change_product_qty = self.stock_change_model.create({
            'location_id': location.id,
            'product_id': product.id,
            'new_quantity': quantity,
        })
        change_product_qty.change_product_qty()
        return change_product_qty

    def create_orderpoint(self):
        """Create a Reordering Rule"""
        self.reorder = self.reordering_rule_model.create({
                                'name': 'Order-point',
                                'product_id': self.product.id,
                                'product_min_qty': '100',
                                'product_max_qty': '500',
                                'qty_multiple': '1'
        })
        return self.reorder

    def create_procurement_orderpoint(self):
        """Make Procurement from Reordering Rule"""
        context = {
                   'active_model': 'stock.warehouse.orderpoint',
                   'active_ids': self.reorder.ids,
                   'active_id': self.reorder.id
                   }
        wizard = self.make_procurement_orderpoint_model.\
            with_context(context).create({})
        wizard.make_procurement()
        return wizard

    def test_security(self):
        """Test Manual Procurement created from Order-Point"""

        # Create Manual Procurement from order-point procured quantity
        self.create_procurement_orderpoint()

        # Assert that Procurement is created with the desired quantity
        self.assertTrue(self.reorder.procurement_ids)
        self.assertEqual(self.reorder.product_id.id,
                         self.reorder.procurement_ids.product_id.id)
        self.assertEqual(self.reorder.name,
                         self.reorder.procurement_ids.origin)
        self.assertNotEqual(self.reorder.procure_recommended_qty,
                            self.reorder.procurement_ids.product_qty)
        self.assertEqual(self.reorder.procurement_ids.product_qty,
                         480.0)
