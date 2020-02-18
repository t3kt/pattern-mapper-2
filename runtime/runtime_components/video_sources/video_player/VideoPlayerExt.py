

from common import ExtensionBase

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

try:
	import tdu
except ImportError:
	tdu = tdu

def onPulse(par):
	name = par.name
	action = tdu.base(name)
	num = tdu.digits(name)
	m = parent()

	if action.startswith('Cue'):
		timepar = getCuePar(num)
		if action == 'Cuetrigger':
			jumpTo(timepar.eval())
		elif action == 'Cueset':
			timepar.val = getCurrentFraction()
	elif action == 'Setrange':
		newstart = getCurrentFraction() if num == 1 else m.par.Timerange1.eval()
		newend = getCurrentFraction() if num == 2 else m.par.Timerange2.eval()
		setTimeRange(newstart, newend)

def setTimeRange(newstart, newend, rescalecues=True):
	m = parent()

	if rescalecues:
		oldstart = m.par.Timerange1.eval()
		oldend = m.par.Timerange2.eval()
		for cuepar in m.pars('Cuepoint*'):
			if cuepar.mode != ParMode.CONSTANT:
				continue
			oldpos = cuepar.eval()
			newpos = tdu.remap(oldpos, oldstart, oldend, newstart, newend)
			cuepar.val = tdu.clamp(newpos, 0, 1)
	m.par.Timerange1 = newstart
	m.par.Timerange2 = newend

def getCuePar(i):
	return getattr(parent().par, 'Cuepoint' + str(i))

def getRangePar(i):
	return getattr(parent().par, 'Timerange' + str(i))

def jumpTo(percent):
	moviein = op('moviefilein')
	moviein.par.cuepoint = percent
	moviein.par.cue.pulse()

def getCurrentFraction():
	return op('info')['index_fraction'][0]

class VideoPlayerCore(ExtensionBase):
	def _SetTimeRange(self, start: float, end: float, rescaleCues=True):
		if rescaleCues:
			oldStart = self.par.Timerange1.eval()
			oldEnd = self.par.Timerange2.eval()
			for cuePar in self.ownerComp.pars('Cuepoint*'):
				if cuePar.mode != ParMode.CONSTANT:
					continue
				oldPos = cuePar.eval()
				newPos = tdu.remap(oldPos, oldStart, oldEnd, start, end)
				cuePar.val = tdu.clamp(newPos, 0, 1)
		self.par.Timerange1.val = start
		self.par.Timerange2.val = end

	def JumpTo(self, percent: float):
		movieIn = self.op('moviefilein')
		movieIn.par.cuepoint = percent
		movieIn.par.cue.pulse()

	def _CuePar(self, i: int):
		return getattr(self.par, f'Cuepoint{i}')

	def _CurrentFraction(self):
		return self.op('info')['index_fraction'][0]

	def OnPulse(self, par: 'Par'):
		action = tdu.base(par.name)
		num = tdu.digits(par.name)
		if action == 'Resetstate':
			self.JumpTo(0)
		elif action.startswith('Cue'):
			timePar = self._CuePar(num)
			if action == 'Cuetrigger':
				self.JumpTo(timePar.eval())
			elif action == 'Cueset':
				timePar.val = self._CurrentFraction()
		elif action == 'Setrange':
			start = self._CurrentFraction() if num == 1 else self.par.Timerange1.eval()
			end = self._CurrentFraction() if num == 2 else self.par.Timerange2.eval()
			self._SetTimeRange(start, end, rescaleCues=True)
