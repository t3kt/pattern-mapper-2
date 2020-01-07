from common import simpleloggedmethod
from pm2_project import PProject, PRenderSettings
from pm2_runtime_shared import RuntimeSubsystem

class PatternRenderer(RuntimeSubsystem):
	@simpleloggedmethod
	def ReadFromProject(self, project: PProject):
		render = project.render or PRenderSettings()
		self.par.Overrideres = render.useCustomRes is True
		self.par.Renderresw = render.renderWidth or self.par.Renderresw.default
		self.par.Renderresh = render.renderHeight or self.par.Renderresh.default
		self.par.Fillenable = render.fillEnable is not False
		self.par.Wireenable = render.wireEnable is not False

	@simpleloggedmethod
	def WriteToProject(self, project: PProject):
		render = project.render or PRenderSettings()
		render.useCustomRes = bool(self.par.Overrideres)
		render.renderWidth = int(self.par.Renderresw)
		render.renderHeight = int(self.par.Renderresh)
		render.fillEnable = bool(self.par.Fillenable)
		render.wireEnable = bool(self.par.Wireenable)
		project.render = render
