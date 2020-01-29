from pm2_runtime_shared import RuntimeComponent, SerializableParams

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class SingleShapeStateSetting(RuntimeComponent, SerializableParams):
	def __init__(self, ownerComp):
		super().__init__(ownerComp)
		self.UpdateParStates()

	def UpdateParStates(self):
		currentFieldDat = self.op('current_field')
		style = currentFieldDat[1, 'style'] if currentFieldDat else None
		self.par.Valfloat.enable = style == 'float'
		self.par.Valint.enable = style == 'int'
		self.par.Valcolorr.enable = style == 'color'
		self.par.Valmenu.enable = style == 'menu'
		self.par.Valvectorx.enable = style == 'xyz'
		if style == 'menu':
			self.par.Valmenu.menuNames = currentFieldDat[1, 'menuNames'].val.split(' ')
			self.par.Valmenu.menuLabels = currentFieldDat[1, 'menuLabels'].val.split(' ')
		else:
			self.par.Valmenu.menuNames = []
			self.par.Valmenu.menuLabels = []
