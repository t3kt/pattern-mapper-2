from typing import List, Optional, Set

from common import ExtensionBase
from pm2_managed_components import ComponentState, ParamState

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class SubComponentSpecBuilder(ExtensionBase):
	@property
	def _Target(self) -> Optional['OP']:
		return self.par.Target.eval()

	# used for par menu
	def GetAllPageNames(self):
		target = self._Target
		if not target:
			return []
		return [
			page.name
			for page in target.customPages
			if not page.name.startswith(':')
		]

	# used for par menu
	def GetAllParNames(self):
		target = self._Target
		if not target:
			return []
		return [
			par.name
			for par in target.customPars
			if not par.label.startswith(':')
		]

	def _GetMatchedPageNames(self):
		return _getFilteredStrings(
			self.GetAllPageNames(),
			self.par.Includepages.eval(),
			self.par.Excludepages.eval(),
		)
	def _GetMatchedParNames(self):
		return _getFilteredStrings(
			self.GetAllParNames(),
			self.par.Includepars.eval(),
			self.par.Excludepars.eval(),
		)

	@property
	def _CompName(self):
		name = self.par.Name
		if name:
			return name.eval()
		target = self._Target
		if target:
			return target.name

	def GetPars(self) -> List['Par']:
		pageNames = self._GetMatchedPageNames()
		if not pageNames:
			return []
		parNames = self._GetMatchedParNames()
		if not parNames:
			return []
		includeOps = self.par.Oppars
		includeFile = self.par.Filepars
		includeReadOnly = self.par.Readonlypars
		includeConst = self.par.Constpars
		includeBound = self.par.Boundpars
		includeExprs = self.par.Exprpars
		matched = []
		for par in self._Target.pars(*parNames):
			if par.page.name not in pageNames:
				continue
			if par.isOP and not includeOps:
				continue
			if par.readOnly and not includeReadOnly:
				continue
			if not includeFile and par.style in ('File', 'Folder'):
				continue
			if par.mode == ParMode.CONSTANT and not includeConst:
				continue
			if par.mode == ParMode.BIND and not includeBound:
				continue
			if par.mode == ParMode.EXPRESSION and not includeExprs:
				continue
			matched.append(par)
		return matched

	def GetParamStates(self) -> List[ParamState]:
		return [
			ParamState.fromPar(par)
			for par in self.GetPars()
		]

	def GetComponentState(self) -> Optional[ComponentState]:
		name = self._CompName
		if not name:
			return None
		return ComponentState(
			name=name,
			params=self.GetParamStates(),
		)

def _getFilteredStrings(names: List[str], includePattern: str, excludePattern: str) -> Set[str]:
	if not names or not includePattern or excludePattern == '*':
		return set()
	if includePattern == '*':
		matched = set(names)
	else:
		matched = set()
		includePatternParts = tdu.split(includePattern)
		for part in includePatternParts:
			matched.update(tdu.match(part, names))
	if not matched:
		return set()
	if not excludePattern:
		return matched
	for part in tdu.split(excludePattern):
		for name in tdu.match(part, names):
			matched.discard(name)
	return matched
