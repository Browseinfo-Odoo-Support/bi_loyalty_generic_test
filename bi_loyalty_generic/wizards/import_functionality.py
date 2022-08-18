from odoo import models, fields, api, _,tools
import xlrd
from odoo.exceptions import UserError, ValidationError,Warning
import time
import tempfile
import binascii
import xlrd
import io

class ManuallyLoyalty(models.TransientModel):
	_name = 'import.loyalty.wizard'
	_description = "Import Functionality Loyalty Wizard "

	file_name = fields.Char()
	file = fields.Binary('File')

	def button_import(self):

		if self.file:
			file_name = str(self.file_name)
			extension = file_name.split('.')[1]
		if extension not in ['xls', 'xlsx', 'XLS', 'XLSX']:
			raise ValidationError(_('Please upload only xls file.!'))
		fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
		fp.write(binascii.a2b_base64(self.file))
		fp.seek(0)
		values = {}
		invoice_ids = []
		workbook = xlrd.open_workbook(fp.name)

		sheet = workbook.sheet_by_index(0)
		line_vals = []
		for row_no in range(sheet.nrows):
			if row_no <= 0:
				fields = map(lambda row: row.value.encode('utf-8'), sheet.row(row_no))
			else:
				line = list(
					map(lambda row: isinstance(row.value, bytes) and row.value.encode('utf-8') or str(row.value),
						sheet.row(row_no)))
				values.update({'partner_id': line[0], 'points': int(float(line[2])), 'trans_type': line[1].lower()})
				vals = self._create_journal_entry(values)
				self.env['all.loyalty.history'].create(vals)

	def _create_journal_entry(self, record):
		partner_id = self.env['res.partner'].search([('name', '=', record.get('partner_id'))], limit=1)
		if not partner_id:
			partner_id = self.env['res.partner'].create({
				'name': record.get('partner_id'),
			})
		line_ids = {
			'partner_id': partner_id.id,
			'points': record.get('points'),
			'transaction_type': record.get('trans_type'),
			'state' : 'done'
		}
		return line_ids