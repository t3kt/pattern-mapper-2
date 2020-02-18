from pm2_settings import *

def settings():
	settings = PSettings(
		preProc=PPreProcSettings(
			recenter=PRecenterSettings(bound=BoundType.frame),
			rescale=PRescaleSettings(bound=BoundType.frame),
			fixTriangleCenters=True,
		),
		# dedup=PDuplicateMergeSettings(
		# 	ignoreDepth=True,
		# ),
		grouping=PGroupingSettings(
			groupGenerators=[
				PIdGroupGenSpec(
					ids=['PanelFacetTop', 'PanelFacetRight', 'PanelFacetLeft']),
				PMergeGroupGenSpec(
					baseName='Panels',
					groups=['PanelFacetTop', 'PanelFacetRight', 'PanelFacetLeft']),
				PIdGroupGenSpec(
					ids=['LeftBars', 'RightBars', 'VerticalBars', 'BarJoints']),
				PMergeGroupGenSpec(
					baseName='BarsNoJoints',
					groups=['LeftBars', 'RightBars', 'VerticalBars']),
				PMergeGroupGenSpec(
					baseName='Bars',
					groups=['LeftBars', 'RightBars', 'VerticalBars', 'BarJoints']),
			]
		),
		sequencing=PSequencingSettings(
			sequenceGenerators=[
				PPathSequenceGenSpec(
					baseName='BarBouncePath',
					pathPath='svg/g[id=BouncePath]/path[id=BouncePath]'),
			]
		),
	)
	for stackNum in range(1, 4):
		partNames = []
		for loopNum in range(1, 5):
			partName = f'VerticalBarRingStack{stackNum}Ring{loopNum}'
			partNames.append(partName)
			settings.sequencing.sequenceGenerators.append(
				PPathSequenceGenSpec(
					baseName=partName,
					pathPath=f'svg/g[id=VerticalRingStackPaths]/g[id=VerticalBarRingStack{stackNum}]/path[id=Loop{loopNum}]',
					attrs=PSequenceGenAttrs(temporary=True),
				))
		settings.sequencing.sequenceGenerators += [
			PParallelSequenceGenSpec(
				baseName=f'VerticalBarRingStack{stackNum}Parallel',
				partNames=partNames),
			PJoinSequenceGenSpec(
				baseName=f'VerticalBarRingStack{stackNum}Sequence',
				partNames=partNames),
			PParallelSequenceGenSpec(
				baseName='VerticalBarRingStacksParallel',
				partNames=[f'VerticalBarRingStack{stackNum}Parallel' for stackNum in range(1, 4)]),
			PJoinSequenceGenSpec(
				baseName='VerticalBarRingStacksSequence',
				partNames=[f'VerticalBarRingStack{stackNum}Parallel' for stackNum in range(1, 4)]),
		]
	return settings
