from pm2_settings import *

def settings():
	return PSettings(
		preProc=PPreProcSettings(
			recenter=PRecenterSettings(bound=BoundType.frame),
			rescale=PRescaleSettings(bound=BoundType.frame),
			fixTriangleCenters=True,
		),
		grouping=PGroupingSettings(
			groupGenerators=[
				PIdGroupGenSpec(
					ids=['orange1', 'orange2'],
					attrs=PGroupGenAttrs(mergeAs='orange'),
				),
				PIdGroupGenSpec(
					ids=['blue1', 'blue2', 'blue3', 'blue4', 'blue5'],
					attrs=PGroupGenAttrs(mergeAs='blue'),
				),
			]
		),
		dedup=PDuplicateMergeSettings(
			ignoreDepth=True,
		),
	)
