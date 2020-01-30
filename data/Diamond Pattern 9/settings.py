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
				PIdGroupGenSpec(ids=['CenterStar']),
				PIdGroupGenSpec(
					ids=['PinkArm{}'.format(i) for i in range(1, 9)],
					attrs=PGroupGenAttrs(mergeAs='PinkArms')
				),
				PIdGroupGenSpec(
					ids=['BlueArm{}'.format(i) for i in range(1, 9)],
					attrs=PGroupGenAttrs(mergeAs='BlueArms')
				),
			]
		),
		sequencing=PSequencingSettings(sequenceGenerators=[]),
	)
	seqGens = []
	for direction in ['CW', 'CCW']:
		seqGens += [
			PPathSequenceGenSpec(
				baseName='BlueRadialPath{}{}'.format(direction, i),
				pathPath='svg/g[id=BlueRadialPaths{}]/path[id=BlueRadialPath{}]'.format(direction, i))
			for i in range(1, 9)
		]
		seqGens.append(
			PJoinSequenceGenSpec(
				'BlueRadialPathsEndOnEnd{}'.format(direction),
				partNames=['BlueRadialPath{}{}'.format(direction, i) for i in range(1, 9)]
			))
		seqGens.append(
			PParallelSequenceGenSpec(
				'BlueRadialPathsParallel{}'.format(direction),
				partNames=['BlueRadialPath{}{}'.format(direction, i) for i in range(1, 9)]
			))
	settings.sequencing.sequenceGenerators = seqGens
	return settings
