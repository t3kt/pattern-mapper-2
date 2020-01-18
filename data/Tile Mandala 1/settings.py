from pm2_settings import *

def settings():
	return PSettings(
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
		grouping=PGroupingSettings(
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
		),
		sequencing=PSequencingSettings(
			sequenceGenerators=[
				PPathSequenceGenSpec(
					baseName='RingSeq{}'.format(i),
					pathPath='svg/g[id=RingPaths]/path[id=RingPath{}]'.format(i)
				)
				for i in range(1, 25)
			]
		),
	)
