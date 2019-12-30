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
		),
		grouping=PGroupingSettings(
			groupGenerators=[
				# PPathGroupGenSpec(
				# 	baseName='DepthLayer1',
				# 	paths=['^.*/g\[id=DepthLayer1\]'],
				# 	depthLayer =
				# ),
				# PPathGroupGenSpec(
				# 	baseName='Corners',
				# 	paths=[r'^.*/g\[id=.*Corner\]'],
				# ),
				# PPathGroupGenSpec(
				# 	baseName='Edges',
				# 	paths=[r'^.*/g\[id=.*Edges\]'],
				# ),
				PIdGroupGenSpec(
					ids=[
						'Corners',
						'Edges',
						'LeftFaces',
						'BottomBackCorner',
						'BottomLeftBackEdge',
						'BottomRightBackEdge',
						'BackEdge',
						'BottomRightCorner',
						'BottomLeftCorner',
						'TopBackCorner',
						'BottomRightFrontEdge',
						'TopRightBackEdge',
						'RightEdge',
						'LeftEdge',
						'BottomLeftFrontEdge',
						'TopBackRightEdge',
						'TopRightCorner',
						'TopLeftCorner',
						'BottomFrontCorner',
						'TopRightFrontEdge',
						'CenterFrontEdge',
						'TopLeftFrontEdge',
						'TopFrontCorner',
					]),
			],
		),
	)
