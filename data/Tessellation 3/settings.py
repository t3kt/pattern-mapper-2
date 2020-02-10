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
				PIdGroupGenSpec(ids=['DiscCenter'])
			] + [
				PIdGroupGenSpec(ids=[f'OuterDisc{i}'])
				for i in range(1, 7)
			] + [
				PIdGroupGenSpec(ids=[f'OuterGear{i}'])
				for i in range(1, 7)
			],
		),
		sequencing=PSequencingSettings(
			sequenceGenerators=[
				PPathSequenceGenSpec(
					baseName=f'TriLoopPath{i}',
					pathPath=f'svg/g[id=TriLoopPaths]/path[id=TriLoopPath{i}]')
				for i in range(1, 3)
			] + [
				PPathSequenceGenSpec(
					baseName=f'WandPath{i}',
					pathPath=f'svg/g[id=WandPaths]/path[id=WandPath{i}]')
				for i in range(1, 4)
			] + [
				PPathSequenceGenSpec(
					baseName='OuterLoopPath',
					pathPath='svg/g[id=OuterLoopPath]/path[0]'
				)
			] + [
				PPathSequenceGenSpec(
					baseName=f'OuterGearPath{i}',
					pathPath=f'svg/g[id=OuterGearPaths]/path[id=OuterGearPath{i}]')
				for i in range(1, 7)
			],
		),
	)
	return settings
