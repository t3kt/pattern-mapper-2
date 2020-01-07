from pm2_settings import *

def settings():
	return PSettings(
		preProc=PPreProcSettings(
			recenter=PRecenterSettings(bound=BoundType.frame),
			rescale=PRescaleSettings(bound=BoundType.frame),
			fixTriangleCenters=True,
		),
		dedup=PDuplicateMergeSettings(
			ignoreDepth=True,
			# tolerance=0.000001,
			equivalence=ShapeEquivalence.points,
			primaryScopes=[PScope(groups=['RightFaces', 'LeftFaces', 'UpFaces'])]
		),
		grouping=PGroupingSettings(
			groupGenerators=[
				PIdGroupGenSpec(
					ids=['RightFaces', 'LeftFaces', 'UpFaces'],
				),
				PIdGroupGenSpec(
					ids=[
						'GreenSections', 'PurpleSections',
						'BluePaths', 'BlueCenter', 'BlueBlocks',
						'PinkPanels', 'OuterGreen',
					],
				),
				PIdGroupGenSpec(
					ids=['RightSlices', 'LeftSlices', 'UpSlices'],
				),
			],
		),
	)
