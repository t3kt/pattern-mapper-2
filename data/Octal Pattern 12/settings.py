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
				PIdGroupGenSpec(ids=['Corners', 'Cross']),
			],
		),
		sequencing=PSequencingSettings(
			sequenceGenerators=[
				PPathSequenceGenSpec(
					baseName='RingPath{}'.format(i),
					pathPath='svg/g[id=RingPaths]/path[{}]'.format(i))
				for i in range(1, 12)
			],
		),
	)
	settings.sequencing.sequenceGenerators += [
		PPathSequenceGenSpec(
			baseName='RingPath{}'.format(i),
			pathPath='svg/g[id=RingPaths]/path[{}]'.format(i))
		for i in range(1, 12)
	]
	settings.sequencing.sequenceGenerators.append(
		PParallelSequenceGenSpec(
			baseName='RingPathsParallel',
			partNames=['RingPath{}'.format(i) for i in range(1, 12)]
		)
	)
	settings.sequencing.sequenceGenerators.append(
		PJoinSequenceGenSpec(
			baseName='RingPathsInOrder',
			partNames=['RingPath{}'.format(i) for i in range(1, 12)],
			flattenParts=True,
		)
	)
	settings.sequencing.sequenceGenerators.append(
		PJoinSequenceGenSpec(
			baseName='RingPathsSequential',
			partNames=['RingPath{}'.format(i) for i in range(1, 12)]
		)
	)
	return settings
