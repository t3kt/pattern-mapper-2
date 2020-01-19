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
		# 	equivalence=ShapeEquivalence.centerRadius,
		# 	# tolerance=0.000001,
		# ),
	)
	settings.grouping = PGroupingSettings(
			groupGenerators=[
				PIdGroupGenSpec(
					ids=[
						'Yellow',
						'Gold',
						'Blue',
						'Teal',
						'Green',
						'Purple',
						'Pink',
					]
				),
				PIdGroupGenSpec(
					ids=['Rings'],
				)
			]
		)
	sequenceGens = []  # type: List[PSequenceGenSpec]
	sequenceGens += [
		PPathSequenceGenSpec(
			baseName='RingSeq{}'.format(i),
			pathPath='svg/g[id=RingPaths]/path[id=RingPath{}]'.format(i)
		)
		for i in range(1, 25)
	]
	sequenceGens += [
		PJoinSequenceGenSpec(
			baseName='RingsSeqEndOnEnd',
			partNames=['RingSeq{}'.format(i) for i in range(1, 25)]
		),
		PJoinSequenceGenSpec(
			baseName='RingsSeqFlat',
			partNames=['RingSeq{}'.format(i) for i in range(1, 25)],
			flattenParts=True,
		),
	]
	settings.sequencing = PSequencingSettings(
			sequenceGenerators=sequenceGens)
	return settings
