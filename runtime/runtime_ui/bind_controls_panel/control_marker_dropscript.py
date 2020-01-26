#
#  arguments for dropping nodes           (and files)
#
#       args[0] dropped node name            (or filename)
#       args[1] x position
#       args[2] y position
#       args[3] dragged index
#       args[4] total dragged
#       args[5] operator                     (or file extension)
#       args[6] dragged node parent network  (or parent directory)
#       args[7] dropped network
#

import os

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from runtime.runtime_ui.bind_controls_panel.BindControlsPanelExt import BindControlsPanel

dropTypeDict = {
	
	'loadAudio' : ['aif','aiff','mp3','wav','ogg','m4a'],
	'loadChan' : ['bchan','bclip','chan','clip'],
	'loadGeo' : ['3ds','dae','dxf','fbx'],
	'loadUsd' : ['usd', 'usda', 'usdc', 'usdz'],
	'loadMidi' : ['mid','midi'],
	'loadSop' : ['bgeo','geo','bhclassic','hclassic','tog','obj'],
	'loadAlm' : ['abc'],
	'loadTable' : ['dat','tsv', 'csv'],
	'loadTop' : ['avi','bmp','flv','gif','hdr','jpeg','jpg','m2ts','m4v','mkv','mov','mp4','mpeg','mpg','mts','png','swf','tga','tif','tiff','tmv','wmv','ffs','dds','mxf','ts','dpx','r3d','fits', 'webm'],
	'loadTopPoints' : ['exr'],
	'loadPoints' : ['ply','xyz','pts'],
	'loadSvg' : ['svg'],
	'loadTox' : ['tox'],
	'loadTxt' : ['bat','cmd','frag','txt','vert','glsl','xml','rtf','py'],
	'loadSbsar' : ['sbsar'],
	'loadDfxdll' : ['dfxdll']
}

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
	return
	newOp = None

	dropDict = locals()
	dropDict['xPos'] = float(dropDict['xPos'])
	dropDict['yPos'] = float(dropDict['yPos'])
	dropDict['dropExt'] = dropDict['dropExt'].lower()
	dropDict['destPath'] = op(dropDict['destPath'])
	dropDict['baseName'] = tdu.legalName(dropDict['baseName'])

	if os.path.isfile(dropDict['dropName']):
		# find extension in dropTypeDict
		funcName = None
		for x in dropTypeDict:
			if dropDict['dropExt'] in dropTypeDict[x]:
				funcName = x
				break

		if funcName:
			newOp = getattr(parent().ext.DragDrop,funcName)(dropDict)
			if newOp:
				ui.status = '{0} loaded into {1} {2}'.format(dropDict['dropName'],newOp.family,newOp.path)
			else:
				ui.status = 'A problem occured while loading {0}.'.format(dropDict['dropName'])
		else:
			ui.status = '{0} of type {1} is not supported.'.format(dropDict['dropName'],dropDict['dropExt'])
	else:
		# this is not a file that is being dropped
		# but a node
		if dropDict['dropExt'] in [x.lower() for x in families]:
			newOp = parent().ext.DragDrop.dropNode(dropDict)
			if newOp:
				ui.status = '{0} was copied to {1}'.format(op(dropDict['baseName']).op(dropDict['dropName']), newOp.path)
			else:
				ui.status = 'A problem occured while copying {0} into {1}'.format(op(dropDict['baseName']).op(dropDict['dropName']), dropDict['destPath'])

		# but a parameter
		elif dropDict['dropExt'] == 'parameter':
			ui.status = 'To drop parameters on a Component, place a custom drop script inside the component and use args[0] to args[7] to specify your own drop behaviour.'

			#parOp= parent().ext.DragDrop.dropPar(dropDict)
			#if parOp:
			#	ui.status = 'A parameter CHOP {0} was created in {1} selecting {2} from {3}'.format(parOp.path,dropDict['destPath'],dropDict['dropName'],dropDict['baseName'])

		# but a channel
		elif dropDict['dropExt'] == 'channel':
			ui.status = 'To drop channels on a Component, place a custom drop script inside the component and use args[0] to args[7] to specify your own drop behaviour.'

			#selectOp = parent().ext.DragDrop.dropChan(dropDict)
			#if selectOp:
			#	ui.status = 'A select CHOP {0} was created in {1} selecting {2} from {3}'.format(selectOp.path,dropDict['destPath'],dropDict['dropName'],dropDict['baseName'])

	return newOp

# try:
if len(args):
  onDrop(*args)
# except:
#     pass
