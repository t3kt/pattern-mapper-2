from typing import Optional, Any

from common import ExtensionBase, loggedmethod
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

	def RemapLocalPaths(self, dat: 'DAT'):
		hostEditor = self.par.Hosteditor.eval()  # type: COMP
		if not hostEditor:
			return
		for cell in dat.col('localPath')[1:]:
			o = hostEditor.op(cell)
			cell.val = o.path if o else ''

	@loggedmethod
	def PrepareParamTable(self, dat: 'DAT', inDat: 'DAT'):
		dat.clear()
		dat.appendRow(['remoteName', 'localName', 'localPath', 'localParam'])
		if inDat.numRows < 2:
			return
		hostEditor = self.par.Hosteditor.eval()  # type: COMP
		if not hostEditor:
			return
		for i in range(1, inDat.numRows):
			localOp = hostEditor.op(inDat[i, 'localPath'])
			if not localOp:
				continue
			par = getattr(localOp.par, inDat[i, 'localParam'].val, None)
			if par is None:
				continue
			dat.appendRow([
				inDat[i, 'remoteName'],
				f'{localOp.name}:{par.name}',
				localOp.path,
				par.name,
			])

	def InitializeEditor(self, namespace: str, messageHandler: MessageHandler, spec: PComponentSpec):
		self.SetTargetName(spec.name)
		self.par.Messagehandler = messageHandler
		for parName, val in spec.pars.items():
			self.SetParVal(parName, val)
		for compName, compPars in spec.subCompPars.items():
			for parName, val in compPars.items():
				self.SetParVal(f'{compName}.{parName}', val)

	def SetTargetName(self, name: str):
		self.par.Targetname = name

	def _GetPar(self, name: str) -> Optional['Par']:
		paramTable = self.op('param_table')  # type: DAT
		localPath = paramTable[name, 'localPath']
		localOp = self.op(localPath) if localPath else None
		if not localOp:
			return None
		localParam = paramTable[name, 'localParam']
		return getattr(localOp.par, localParam.val) if localParam else None

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
		localName = f'{par.owner.name}:{par.name}'
		remoteName = self.op('params_by_local_name')[localName, 'remoteName']
		if not remoteName:
			self._LogEvent(f'Remote param not found for {par!r}')
			return
		# self._LogEvent(f'Remote param found: {remoteName}')
		self.SendMessage(
			CommonMessages.setPar,
			data=[
				self.par.Targetname.eval(),
				remoteName.val,
				par.eval(),
			]
		)

	def SendMessage(self, name: str, data: Any = None, namespace: str = None):
		handler = self.par.Messagehandler.eval()  # type: MessageHandler
		if not handler:
			return
		handler.HandleMessage(Message(
			name,
			data,
			namespace=namespace or str(self.par.Messagenamespace)))
