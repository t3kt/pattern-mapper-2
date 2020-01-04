from pm2_project import PProject, PRenderSettings
from pm2_runtime_shared import RuntimeSubsystem

class PatternRenderer(RuntimeSubsystem):
	def ReadFromProject(self, project: PProject):
		render = project.render or PRenderSettings()
		self.par.Renderresw = render.renderWidth or self.par.Renderresw.default
		self.par.Renderresh = render.renderHeight or self.par.Renderresh.default
		self.par.Fillenable = render.fillEnable is not False
		self.par.Wireenable = render.wireEnable is not False

	def WriteToProject(self, project: PProject):
		render = project.render or PRenderSettings()
		render.renderWidth = int(self.par.Renderresw)
		render.renderHeight = int(self.par.Renderresh)
		render.fillEnable = bool(self.par.Fillenable)
		render.wireEnable = bool(self.par.Wireenable)
		project.render = render
