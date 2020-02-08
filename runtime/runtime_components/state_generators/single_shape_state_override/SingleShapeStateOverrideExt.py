from typing import Union

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from runtime.runtime_components.single_shape_state_setting.SingleShapeStateSettingExt import SingleShapeStateSetting

def UpdateParStates(comp: 'COMP'):
	setting = comp.op('single_shape_state_setting')  # type: Union['COMP', SingleShapeStateSetting]
	setting.UpdateParStates()
	comp.par.Valfloat.enable = setting.par.Valfloat.enable
	comp.par.Valint.enable = setting.par.Valint.enable
	comp.par.Valcolorr.enable = setting.par.Valcolorr.enable
	comp.par.Valmenu.enable = setting.par.Valmenu.enable
	comp.par.Valvectorx.enable = setting.par.Valvectorx.enable
	comp.par.Valmenu.menuNames = setting.par.Valmenu.menuNames
	comp.par.Valmenu.menuLabels = setting.par.Valmenu.menuLabels
