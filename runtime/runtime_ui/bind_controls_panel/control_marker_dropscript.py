# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from runtime.runtime_ui.bind_controls_panel.BindControlsPanelExt import BindControlsPanel

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
	host = ext.BindControlsPanel  # type: BindControlsPanel
	host.OnMarkerDrop(
		dropName, index, totalDragged, dropExt, baseName, destPath
	)

if len(args):
	onDrop(*args)
