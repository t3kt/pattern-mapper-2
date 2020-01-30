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
		sequencing=PSequencingSettings(
			sequenceGenerators=
			[
				PPathSequenceGenSpec(
					baseName='BlueRadialPathCW{}'.format(i),
					pathPath='svg/g[id=BlueRadialPathsCW]/path[id=BlueRadialPath{}]'.format(i)
				)
				for i in range(1, 9)
			] + [
				PPathSequenceGenSpec(
					baseName='BlueRadialPathCCW{}'.format(i),
					pathPath='svg/g[id=BlueRadialPathsCCW]/path[id=BlueRadialPath{}]'.format(i)
				)
				for i in range(1, 9)
			]
		),
	)
