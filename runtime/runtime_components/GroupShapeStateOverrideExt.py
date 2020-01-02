from pm2_project import POverrideShapeStateSpec
from pm2_runtime_shared import ShapeStateExt

class GroupShapeStateOverrider(ShapeStateExt):
	def SetSpec(self, spec: POverrideShapeStateSpec):
		self.par.Groups = spec.groupName or '*'
		self.par.Invertmask = spec.invertMask is True
		self.par.Enableoverride = spec.enable is not False
		self.par.Overrideamount = spec.amount if spec.amount is not None else 1
		self.SetShapeState(spec.shapeState)

	def GetSpec(self):
		return POverrideShapeStateSpec(
			groupName=str(self.par.Groups),
			enable=bool(self.par.Enableoverride),
			amount=float(self.par.Overrideamount),
			invertMask=bool(self.par.Invertmask),
			shapeState=self.GetShapeState(),
		)

