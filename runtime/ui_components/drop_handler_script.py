# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from pm2_ui import DropReceiver

# the drop function takes the following arguments and according to the dropped type
# calls a function in the /sys attached DragDrop extension
#
# dropName: dropped node name or filename
# [x/y]Pos: position in network pane
# index: index of dragged item
# totalDragged: total amount of dragged items
# dropExt: operator type or file extension of dragged item
# baseName: dragged node parent network or parent directory of dragged file
# destPath: dropped network

def onDrop(dropName, xPos, yPos, index, totalDragged, dropExt, baseName, destPath):
	host = ext.DropReceiver  # type: DropReceiver
	host.HandleDrop(
		dropName=dropName,
		dropExt=dropExt,
		baseName=baseName,
		destPath=destPath,
	)

if len(args):
	onDrop(*args)
