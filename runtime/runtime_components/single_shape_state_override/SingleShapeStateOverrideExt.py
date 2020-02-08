from typing import Union

from common import ExtensionBase

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from runtime.runtime_components.single_shape_state_setting.SingleShapeStateSettingExt import SingleShapeStateSetting

class SingleShapeStateOverride(ExtensionBase):
	def __init__(self, ownerComp):
		super().__init__(ownerComp)
		self.UpdateParStates()

	def UpdateParStates(self):
		setting = self.op('single_shape_state_setting')  # type: Union['COMP', SingleShapeStateSetting]
		setting.UpdateParStates()
		self.par.Valfloat.enable = setting.par.Valfloat.enable
		self.par.Valint.enable = setting.par.Valint.enable
		self.par.Valcolorr.enable = setting.par.Valcolorr.enable
		self.par.Valmenu.enable = setting.par.Valmenu.enable
		self.par.Valvectorx.enable = setting.par.Valvectorx.enable
		self.par.Valmenu.menuNames = setting.par.Valmenu.menuNames
		self.par.Valmenu.menuLabels = setting.par.Valmenu.menuLabels
