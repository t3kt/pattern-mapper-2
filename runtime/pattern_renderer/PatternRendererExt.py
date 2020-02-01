from typing import List

from common import simpleloggedmethod
from pm2_messaging import Message, MessageHandler
from pm2_project import PProject, PRenderSettings
from pm2_runtime_shared import RuntimeSubsystem, SerializableParamsOrCOMP

class PatternRenderer(RuntimeSubsystem, MessageHandler):
	@property
	def _TextureDefinitions(self) -> List['SerializableParamsOrCOMP']:
		return self.ops('texture_def_*')

	@simpleloggedmethod
	def ReadFromProject(self, project: PProject):
		render = project.render or PRenderSettings()
		self.par.Overrideres = render.useCustomRes is True
		self.par.Renderresw = render.renderWidth or self.par.Renderresw.default
		self.par.Renderresh = render.renderHeight or self.par.Renderresh.default
		self.par.Fillenable = render.fillEnable is not False
		self.par.Wireenable = render.wireEnable is not False
		self.par.Wirewidth = render.wireWidth if render.wireWidth is not None else self.par.Wirewidth.default
		texDefSettings = render.textures or []
		for texDef in self._TextureDefinitions:
			texIndex = int(texDef.par.Textureindex)
			texDef.SetParDict(texDefSettings[texIndex] if texIndex < len(texDefSettings) else {})

	@simpleloggedmethod
	def WriteToProject(self, project: PProject):
		render = project.render or PRenderSettings()
		render.useCustomRes = bool(self.par.Overrideres)
		render.renderWidth = int(self.par.Renderresw)
		render.renderHeight = int(self.par.Renderresh)
		render.fillEnable = bool(self.par.Fillenable)
		render.wireEnable = bool(self.par.Wireenable)
		render.wireWidth = float(self.par.Wirewidth)
		render.textures = [
			texDef.GetParDict()
			for texDef in self._TextureDefinitions
		]
		project.render = render

	def HandleMessage(self, message: Message):
		pass
