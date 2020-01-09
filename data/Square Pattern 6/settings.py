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
			groupGenerators=
			[
				PIdGroupGenSpec(
					ids=[n],
					# TODO: fix the grouping depth thing
				)
				for n, groupAt in [
					('1.a', 2),
					('1.b', 2),
					('2.a', 2),
					('2.b', 3),
					('2.c', 2),
					('3.a', 4),
					('3.b', 3),
					('3.c', 2),
				]
			]
		),
	)
