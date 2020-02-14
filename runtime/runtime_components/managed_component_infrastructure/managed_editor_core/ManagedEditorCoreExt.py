from typing import Optional, Dict, Any

from common import ExtensionBase
from pm2_managed_components import ManagedComponentEditorInterface
from pm2_messaging import CommonMessages, MessageHandler, Message
from pm2_project import PComponentSpec

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class ManagedEditorCore(ExtensionBase, ManagedComponentEditorInterface):
	def __init__(self, ownerComp):
		super().__init__(ownerComp)
		self.nameToParamMap = {}  # type: Dict[str, Par]
		self.paramToNameMap = {}  # type: Dict[Par, str]

	def _InitializeParams(self):
		self.nameToParamMap.clear()
		self.paramToNameMap.clear()
		paramTable = self.op('param_table')  # type: DAT
		hostEditor = self.par.Hosteditor.eval()  # type: COMP
		for i in range(1, paramTable.numRows):
			localPath = paramTable[i, 'localPath'].val
			localOp = hostEditor.op(localPath)
			if not localOp:
				self._LogEvent(f'WARNING: local param op not found: {localPath}')
				continue
			localParName = paramTable[i, 'localParam'].val
			if not hasattr(localOp.par, localParName):
				self._LogEvent(f'WARNING local param {localParName} not found in {localOp.path}')
				continue
			localPar = getattr(localOp.par, localParName)  # type: Par
			remoteName = paramTable[i, 'remoteName'].val
			self.nameToParamMap[remoteName] = localPar
			self.paramToNameMap[localPar] = remoteName

	def InitializeEditor(self, namespace: str, messageHandler: MessageHandler, spec: PComponentSpec):
		self.SetTargetName(spec.name)
		self._InitializeParams()
		self.par.Messagehandler = messageHandler
		for parName, val in spec.pars.items():
			self.SetParVal(parName, val)
		for compName, compPars in spec.subCompPars.items():
			for parName, val in compPars.items():
				self.SetParVal(f'{compName}.{parName}', val)

	def SetTargetName(self, name: str):
		self.par.Targetname = name

	def _GetPar(self, name: str) -> Optional['Par']:
		return self.nameToParamMap.get(name)

	def SetParVal(self, name: str, val):
		par = self._GetPar(name)
		if par is None:
			self._LogEvent(f'par not found: {name!r}')
			return
		if par.mode != ParMode.CONSTANT:
			self._LogEvent(f'par {name!r} mode is not constant: {par.mode}')
			return
		par.val = val

	def OnLocalParChange(self, par: 'Par'):
		remoteName = self.paramToNameMap.get(par)
		if not remoteName:
			return
		self.SendMessage(
			CommonMessages.setPar,
			data=[remoteName, par.eval()]
		)

	def SendMessage(self, name: str, data: Any = None, namespace: str = None):
		handler = self.par.Messagehandler.eval()  # type: MessageHandler
		if not handler:
			return
		handler.HandleMessage(Message(
			name,
			data,
			namespace=namespace or str(self.par.Messagenamespace)))
