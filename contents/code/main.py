# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyKDE4.kdecore import KAuth, KGlobal
from PyKDE4.kdeui import KPageDialog, KDialog
from PyKDE4.plasma import Plasma
from PyKDE4 import plasmascript
import os.path, os

def readCpuData(number, fileName):
	args = {}
	args["procnumb"] = QString(number)
	args["filename"] = QString(fileName)

	act = KAuth.Action('org.freedesktop.auth.cpufrequtility.read')
	act.setHelperID('org.freedesktop.auth.cpufrequtility')
	act.setArguments(args)
	#print act.hasHelper(), 'ready', act.helperID(), act.name(), 'Valid is', act.isValid()
	reply = act.execute()
	if (reply.failed()) :
		QMessageBox.information(None, "Error", \
					QString("KAuth returned an error code: %1 \n %2").arg(reply.errorCode()).arg(reply.errorDescription()))
		reply.setData(QVariant({QString('contents') : 0}).toMap())
		#print [reply.data()]
	else :
		#print reply.data(), 'reply from :', act.hasHelper(), act.name(), 'Valid is', act.isValid()
		pass
	return reply

def writeCpuData(number, fileName, parametr):
	args = {}
	args["procnumb"] = number
	args["filename"] = fileName
	args["parametr"] = parametr

	act = KAuth.Action('org.freedesktop.auth.cpufrequtility.write')
	act.setHelperID('org.freedesktop.auth.cpufrequtility')
	act.setArguments(args)
	reply = act.execute()
	if (reply.failed()) :
		QMessageBox.information(None, "Error", \
					QString("KAuth returned an error code: %1 \n %2").arg(reply.errorCode()).arg(reply.errorDescription()))
	else :
		#print reply.data(), 'reply from :', act.hasHelper(), act.name(), 'Valid is', act.isValid()
		pass
	return reply

"""
/sys/devices/system/cpu/cpu*/cpufreq/scaling_available_frequencies
		contents available freq* (2001 2000 1600 1200 800)
/sys/devices/system/cpu/cpu*/cpufreq/scaling_available_governors
		contents available governor regimes
/sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
		for change regime
/sys/devices/system/cpu/cpu*/cpufreq/scaling_cur_freq
		current freq (for ex.: 800)
/sys/devices/system/cpu/cpu*/cpufreq/scaling_max_freq
		current max freq
/sys/devices/system/cpu/cpu*/cpufreq/scaling_min_freq
		current min freq
/sys/devices/system/cpu/cpu*/online
		enable\disable(1\0) proc, not for cpu0
/sys/devices/system/cpu/possible
		check possible proc (for ex.: 0-1)
/sys/devices/system/cpu/present
		check present proc (for ex.: 0-1)
"""

def define_proc_data():
	COUNT_PROCESSOR = os.sysconf('SC_NPROCESSORS_ONLN')
	procData = {}
	_count = readCpuData('null', 'possible')
	count = _count.data()[QString('contents')].toString().replace('\n', '').split('-')
	_present = readCpuData('null', 'present')
	present = _present.data()[QString('contents')].toString().replace('\n', '').split('-')
	#print len(count), COUNT_PROCESSOR, ":", [str(present[i]) for i in xrange(len(present))]
	global COUNT_PROC
	if _count.failed() or _present.failed() :
		COUNT_PROC = 0
		procData['count'] = COUNT_PROC
		return procData
	COUNT_PROC = max(COUNT_PROCESSOR, len(count))
	procData['count'] = COUNT_PROC
	procData['availableFreqs'] = {int(i) : readCpuData(str(i), 'available_frequencies') for i in xrange(COUNT_PROC)}
	#print [procData['availableFreqs'][i].data()[QString('contents')].toString() for i in xrange(COUNT_PROC)]
	procData['availableGovernors'] = {int(i) : readCpuData(str(i), 'available_governors') for i in xrange(COUNT_PROC)}
	#print [procData['availableGovernors'][i].data()[QString('contents')].toString() for i in xrange(COUNT_PROC)]
	procData['currentFreq'] = {int(i) : readCpuData(str(i), 'cur_freq') for i in xrange(COUNT_PROC)}
	#print [procData['currentFreq'][i].data()[QString('contents')].toString() for i in xrange(COUNT_PROC)]
	procData['currentGovernor'] = {int(i) : readCpuData(str(i), 'governor') for i in xrange(COUNT_PROC)}
	#print [procData['currentGovernor'][i].data()[QString('contents')].toString() for i in xrange(COUNT_PROC)]
	procData['currentMaxFreq'] = {int(i) : readCpuData(str(i), 'max_freq') for i in xrange(COUNT_PROC)}
	#print [procData['currentMaxFreq'][i].data()[QString('contents')].toString() for i in xrange(COUNT_PROC)]
	procData['currentMinFreq'] = {int(i) : readCpuData(str(i), 'min_freq') for i in xrange(COUNT_PROC)}
	#print [procData['currentMinFreq'][i].data()[QString('contents')].toString() for i in xrange(COUNT_PROC)]
	""" WARNING : /sys/devices/system/cpu/cpu0/online not exist anyway """
	procData['online'] = {int(i) : readCpuData(str(i), 'online') for i in xrange(COUNT_PROC)}
	#print [(i, procData['online'][int(i)].data()[QString('contents')].toString()) for i in xrange(COUNT_PROC)]
	return procData

class plasmaCpuFreqUtility(plasmascript.Applet):
	def __init__(self, parent = None):
		plasmascript.Applet.__init__(self, parent)

		self.kdehome = unicode(KGlobal.dirs().localkdedir())

		if os.path.exists('/usr/share/kde4/apps/plasma/plasmoids/kde-plasma-cpufrequtility/contents/icons/performance.png') :
			self.iconPath = '/usr/share/kde4/apps/plasma/plasmoids/kde-plasma-cpufrequtility/contents/icons/performance.png'
		elif os.path.exists(self.kdehome + '/share/apps/plasma/plasmoids/kde-plasma-cpufrequtility/contents/icons/performance.png') :
			self.iconPath = self.kdehome + '/share/apps/plasma/plasmoids/kde-plasma-cpufrequtility/contents/icons/performance.png'
			#print 'installing', self.iconPath
		else :
			self.iconPath = os.getcwd() + '/plasmaCpuFreqUtility/contents/icons/performance.png'

		self.Settings = QSettings('kde-plasma-cpufrequtility', 'kde-plasma-cpufrequtility')

	def init(self):
		self.setImmutability(Plasma.Mutable)
		self.setHasConfigurationInterface(True)
		self.layout = QGraphicsLinearLayout(self.applet)
		self.layout.setSpacing(0)
		self.icon = Plasma.IconWidget()
		self.icon.setIcon(self.iconPath)
		self.icon.setMinimumIconSize(QSizeF(24.0, 24.0))
		self.icon.clicked.connect(self.mouseDoubleClickEvent)
		self.layout.addItem(self.icon)
		self.setLayout(self.layout)
		self.colorSelect = ColorWidget(self)

		enabled = self.Settings.value('Remember', 0).toInt()[0]
		if bool(enabled) :
			self.ProcData = self.getLastProcParemeters()
			self.Control = ControlWidget({}, self, os.path.dirname(self.iconPath))
			self.Control.changeRegime(self.ProcData)
		else :
			self.ProcData = define_proc_data()
			self.Control = ControlWidget(self.ProcData, self, os.path.dirname(self.iconPath))
			self.setTooltip(self.Control.getNewProcParemeters())

	def mouseDoubleClickEvent(self, ev = True):
		if type(ev) is not bool : ev.ignore()
		if self.Control.isVisible() :
			self.Control.hide()
		else:
			self.Control.move(self.popupPosition(self.Control.size()))
			self.Control.show()

	def parametersReset(self):
		self.Control.close()
		self.ProcData = define_proc_data()
		self.Control = ControlWidget(self.ProcData, self, os.path.dirname(self.iconPath))
		self.setTooltip(self.Control.getNewProcParemeters())
		#self.mouseDoubleClickEvent()

	def setTooltip(self, newParameters):
		htmlStr = '<b>'
		for i in xrange(COUNT_PROC) :
			if i == 0 or newParameters[i]['enable'] == 1 :
				enable = '<font color=' + self.colorSelect.enableOnColor + '> on </font>'
			elif newParameters[i]['enable'] == 0 :
				enable = '<font color=' + self.colorSelect.enableOffColor + '> off </font>'
			htmlStr += '<pre><font color=' + self.colorSelect.cpuColor + '>CPU' + str(i) + '</font>' + enable
			htmlStr += ' <font color=' + self.colorSelect.governorColor + '>' + newParameters[i]['regime'] + '</font>'
			htmlStr += ' <font color=' + self.colorSelect.minFreqColor + '>' + newParameters[i]['minfrq'][:-3] + '</font>'
			htmlStr += ' <font color=' + self.colorSelect.maxFreqColor + '>' + newParameters[i]['maxfrq'][:-3] + '</font><br></pre>'
		htmlStr += '</b>'
		Plasma.ToolTipManager.self().setContent( self.applet, Plasma.ToolTipContent( \
								'CPU FreqUtility', \
								QString(htmlStr), self.icon.icon() ) )

	def getLastProcParemeters(self):
		lastParameters = {}
		i = 0
		for paramProc in self.Settings.value('Parameters', '').toString().split(";;", QString.SkipEmptyParts) :
			lastParameters[i] = {}
			parameters = paramProc.split(" ", QString.SkipEmptyParts)
			lastParameters[i]['enable'] = int(parameters[0])
			lastParameters[i]['regime'] = str(parameters[1])
			lastParameters[i]['minfrq'] = str(parameters[2])
			lastParameters[i]['maxfrq'] = str(parameters[3])
			i += 1
		return lastParameters

	def createConfigurationInterface(self, parent):
		self.colorSelect = ColorWidget(self, parent)
		parent.addPage(self.colorSelect, "Color")
		self.connect(parent, SIGNAL("okClicked()"), self.configAccepted)
		self.connect(parent, SIGNAL("cancelClicked()"), self.configDenied)

	def showConfigurationInterface(self):
		self.dialog = KPageDialog()
		self.dialog.setModal(True)
		self.dialog.setFaceType(KPageDialog.List)
		self.dialog.setButtons( KDialog.ButtonCode(KDialog.Ok | KDialog.Cancel) )
		self.createConfigurationInterface(self.dialog)
		self.dialog.move(self.popupPosition(self.dialog.sizeHint()))
		self.dialog.exec_()

	def configAccepted(self):
		self.colorSelect.refreshInterfaceSettings()
		self.dialog.done(0)
		self.parametersReset()

	def configDenied(self):
		self.dialog.done(0)

class ControlWidget(Plasma.Dialog):
	def __init__(self, procData, obj, iconDir, parent = None):
		Plasma.Dialog.__init__(self, parent)
		self.prnt = obj
		self.ProcData = procData

		self.layout = QGridLayout()
		self.layout.setSpacing(0)
		#print [self.ProcData]
		if len(procData) == 0 or self.ProcData['count'] == 0 :
			self.errorLabel = QLabel('<font color=red size=7>ERROR</font>')
			self.layout.addWidget(self.errorLabel, 0, 0, 2, 4, Qt.AlignCenter)
			self.setLayout(self.layout)
			return None

		self.rememberBox = QCheckBox()
		self.rememberBox.setToolTip('Restore the last state')
		enabled = self.prnt.Settings.value('Remember', 0).toInt()[0]
		if bool(enabled) :
			self.rememberBox.setCheckState(Qt.Checked)
		else :
			self.rememberBox.setCheckState(Qt.Unchecked)

		self.accept = QPushButton()
		self.accept.setText('Apply')
		self.accept.clicked.connect(self.changeRegime)
		#self.accept.setMaximumHeight(20)
		self.reset = QPushButton()
		self.reset.setText("Reset")
		self.reset.clicked.connect(self.prnt.parametersReset)
		#self.reset.setMaximumHeight(20)

		self.buttonPanel = QGridLayout()
		self.buttonPanel.addWidget(self.reset, 0, 0)
		self.buttonPanel.addWidget(self.accept, 0, 1)
		self.minLabel = QLabel('<font color=' + self.prnt.colorSelect.minFreqColor + '>MinFreq</font>')
		self.maxLabel = QLabel('<font color=' + self.prnt.colorSelect.maxFreqColor + '>MaxFreq</font>')

		self.layout.addWidget(self.rememberBox, 0, 1, Qt.AlignCenter)
		self.layout.addItem(self.buttonPanel, 0, 2)
		self.layout.addWidget(self.minLabel, 0, 3, Qt.AlignCenter)
		self.layout.addWidget(self.maxLabel, 0, 4, Qt.AlignCenter)

		self.cpuLabel = {}
		self.cpuEnable = {}
		self.comboGovernorMenu = {}
		self.comboMinFreq = {}
		self.comboMaxFreq = {}
		for i in xrange(COUNT_PROC) :
			self.cpuLabel[i] = QLabel('<font color=' + self.prnt.colorSelect.cpuColor + '>CPU' + str(i) + '</font>')
			self.layout.addWidget(self.cpuLabel[i], 1 + i, 0)

			self.cpuEnable[i] = QCheckBox()
			if i != 0 and i in self.ProcData['online'] :
				enabled = int(self.ProcData['online'][i].data()[QString('contents')].toString().replace('\n', ''))
				#print enabled, i, ' : online'
			else :
				enabled = 0
				if i != 0 : print enabled, i, 'disabled'
			if i == 0 :
				#print 1, i, ' : online'
				self.cpuEnable[i].setCheckState(Qt.Checked)
				self.cpuEnable[i].setEnabled(False)
			else :
				if enabled == 1 :
					self.cpuEnable[i].setCheckState(Qt.Checked)
				if enabled == 0 :
					self.cpuEnable[i].setCheckState(Qt.Unchecked)
				if not i in self.ProcData['online'] :
					self.cpuEnable[i].setEnabled(False)
			self.layout.addWidget(self.cpuEnable[i], 1 + i, 1)

			self.comboGovernorMenu[i] = QComboBox(self)
			if i in self.ProcData['online'] :
				_availableGovernors = self.ProcData['availableGovernors'][i].data()[QString('contents')].toString().replace('\n', '')
			else : _availableGovernors = QString('default')
			availableGovernors = QStringList(_availableGovernors.split(' ', QString.SkipEmptyParts))
			availableGovernors.append('powersave')
			availableGovernors.append('conservative')
			#for item in availableGovernors : print '\t', item
			if i in self.ProcData['online'] :
				currentGovernor = self.ProcData['currentGovernor'][i].data()[QString('contents')].toString().replace('\n', '')
			else : currentGovernor = 'default'
			currGovernorIdx = availableGovernors.indexOf(currentGovernor)
			availableGovernors.removeDuplicates()
			for governor in availableGovernors :
				if os.path.isfile(iconDir + '/' + governor + '.png') :
					path_ = iconDir + '/' + governor + '.png'
				else :
					path_ = iconDir + '/ondemand.png'
				self.comboGovernorMenu[i].addItem(QIcon(path_), governor)
				if governor == currentGovernor : self.prnt.icon.setIcon(path_)
			#print [currentGovernor], currGovernorIdx, [item for item in availableGovernors]
			self.comboGovernorMenu[i].setCurrentIndex(currGovernorIdx)
			self.comboGovernorMenu[i].setEditable(False)
			self.layout.addWidget(self.comboGovernorMenu[i], 1 + i, 2)

			self.comboMinFreq[i] = QComboBox(self)
			#self.comboMinFreq[i].setMinimumContentsLength(8)
			if i in self.ProcData['online'] :
				_availableFreqs = self.ProcData['availableFreqs'][i].data()[QString('contents')].toString().replace('\n', '')
			else : _availableFreqs = QString('')
			availableFreqs = QStringList(_availableFreqs.split(' ', QString.SkipEmptyParts))
			#for item in availableFreqs : print '\t', item
			for j in availableFreqs :
				if j == 'default' : continue
				self.comboMinFreq[i].addItem(str(j)[:-3])
			self.comboMinFreq[i].addItem('default')
			if i in self.ProcData['online'] :
				currentMinFreq = self.ProcData['currentMinFreq'][i].data()[QString('contents')].toString().replace('\n', '')
			else : currentMinFreq = 'default'
			currMinFreqIdx = availableFreqs.indexOf(currentMinFreq)
			self.comboMinFreq[i].setCurrentIndex(currMinFreqIdx)
			self.layout.addWidget(self.comboMinFreq[i], 1 + i, 3)

			self.comboMaxFreq[i] = QComboBox(self)
			#self.comboMaxFreq[i].setMinimumContentsLength(8)
			if i in self.ProcData['online'] :
				_availableFreqs = self.ProcData['availableFreqs'][i].data()[QString('contents')].toString().replace('\n', '')
			else : _availableFreqs = QString('')
			availableFreqs = QStringList(_availableFreqs.split(' ', QString.SkipEmptyParts))
			#for item in availableFreqs : print '\t', item
			for j in availableFreqs :
				if j == 'default' : continue
				self.comboMaxFreq[i].addItem(str(j)[:-3])
			self.comboMaxFreq[i].addItem('default')
			if i in self.ProcData['online'] :
				currentMaxFreq = self.ProcData['currentMaxFreq'][i].data()[QString('contents')].toString().replace('\n', '')
			else : currentMaxFreq = 'default'
			currMaxFreqIdx = availableFreqs.indexOf(currentMaxFreq)
			self.comboMaxFreq[i].setCurrentIndex(currMaxFreqIdx)
			self.layout.addWidget(self.comboMaxFreq[i], 1 + i, 4)

		self.setLayout(self.layout)

	def getNewProcParemeters(self):
		newParameters = {}
		for i in xrange(COUNT_PROC) :

			newParameters[i] = {}
			""" WARNING : /sys/devices/system/cpu/cpu0/online not exist anyway """
			if i != 0 :
				newParameters[i]['enable'] = int(self.cpuEnable[i].checkState())/2
			else :
				newParameters[i]['enable'] = 1
			newParameters[i]['regime'] = self.comboGovernorMenu[i].currentText()
			value = self.comboMinFreq[i].currentText()
			if value != 'default' : value += '000'
			newParameters[i]['minfrq'] = value
			value = self.comboMaxFreq[i].currentText()
			if value != 'default' : value += '000'
			newParameters[i]['maxfrq'] = value

		return newParameters

	def changeRegime(self, data = None):
		if type(data) is dict :
			global COUNT_PROC
			COUNT_PROC = len(data)
			newParameters = data
		else :
			newParameters = self.getNewProcParemeters()
		paramProc = ''
		for i in xrange(COUNT_PROC) :
			paramProc += str(newParameters[i]['enable']) + ' ' + \
						 newParameters[i]['regime'] + ' ' + \
						 newParameters[i]['minfrq'] + ' ' + \
						 newParameters[i]['maxfrq'] + ';;'
			""" WARNING : /sys/devices/system/cpu/cpu0/online not exist anyway """
			if i != 0 :
				#print i, 'online', newParameters[i]['enable']
				writeCpuData(i, 'online', newParameters[i]['enable'])
				""" continue -- because files for this proc not exists already """
				if newParameters[i]['enable'] == 0 : continue
			""" 'default' ignored for set system defaults for current proc"""
			#print i, 'governor', newParameters[i]['regime']
			if newParameters[i]['regime'] != 'default' : writeCpuData(i, 'governor', newParameters[i]['regime'])
			#print i, 'min_freq', newParameters[i]['minfrq']
			if newParameters[i]['minfrq'] != 'default' : writeCpuData(i, 'min_freq', newParameters[i]['minfrq'])
			#print i, 'max_freq', newParameters[i]['maxfrq']
			if newParameters[i]['maxfrq'] != 'default' : writeCpuData(i, 'max_freq', newParameters[i]['maxfrq'])

		if type(data) is not dict :
			if self.rememberBox.checkState() == Qt.Checked :
				self.prnt.Settings.setValue('Remember', 1)
				self.prnt.Settings.setValue('Parameters', paramProc)
			else :
				self.prnt.Settings.setValue('Remember', 0)
				self.prnt.Settings.setValue('Parameters', '')
			self.prnt.Settings.sync()
		self.prnt.parametersReset()

class ColorWidget(QWidget):
	def __init__(self, obj = None, parent= None):
		QWidget.__init__(self, parent)

		self.prnt = parent
		self.Settings = obj.Settings
		colorNames = QColor().colorNames()
		self.initVar()

		self.layout = QGridLayout()

		self.cpuColorLabel = QLabel('cpuColor :')
		self.layout.addWidget(self.cpuColorLabel, 0, 0)
		self.cpuColorBox = QComboBox()
		self.cpuColorBox.setMaximumWidth(150)
		self.cpuColorBox.addItems(colorNames)
		self.cpuColorBox.setCurrentIndex(self.cpuColorBox.findText(self.cpuColor))
		self.layout.addWidget(self.cpuColorBox, 0, 1)

		self.enableOnColorLabel = QLabel('enableOnColor :')
		self.layout.addWidget(self.enableOnColorLabel, 1, 0)
		self.enableOnColorBox = QComboBox()
		self.enableOnColorBox.setMaximumWidth(150)
		self.enableOnColorBox.addItems(colorNames)
		self.enableOnColorBox.setCurrentIndex(self.enableOnColorBox.findText(self.enableOnColor))
		self.layout.addWidget(self.enableOnColorBox, 1, 1)

		self.enableOffColorLabel = QLabel('enableOffColor :')
		self.layout.addWidget(self.enableOffColorLabel, 2, 0)
		self.enableOffColorBox = QComboBox()
		self.enableOffColorBox.setMaximumWidth(150)
		self.enableOffColorBox.addItems(colorNames)
		self.enableOffColorBox.setCurrentIndex(self.enableOffColorBox.findText(self.enableOffColor))
		self.layout.addWidget(self.enableOffColorBox, 2, 1)

		self.governorColorLabel = QLabel('governorColor :')
		self.layout.addWidget(self.governorColorLabel, 3, 0)
		self.governorColorBox = QComboBox()
		self.governorColorBox.setMaximumWidth(150)
		self.governorColorBox.addItems(colorNames)
		self.governorColorBox.setCurrentIndex(self.governorColorBox.findText(self.governorColor))
		self.layout.addWidget(self.governorColorBox, 3, 1)

		self.maxFreqColorLabel = QLabel('maxFreqColor :')
		self.layout.addWidget(self.maxFreqColorLabel, 4, 0)
		self.maxFreqColorBox = QComboBox()
		self.maxFreqColorBox.setMaximumWidth(150)
		self.maxFreqColorBox.addItems(colorNames)
		self.maxFreqColorBox.setCurrentIndex(self.maxFreqColorBox.findText(self.maxFreqColor))
		self.layout.addWidget(self.maxFreqColorBox, 4, 1)

		self.minFreqColorLabel = QLabel('minFreqColor :')
		self.layout.addWidget(self.minFreqColorLabel, 5, 0)
		self.minFreqColorBox = QComboBox()
		self.minFreqColorBox.setMaximumWidth(150)
		self.minFreqColorBox.addItems(colorNames)
		self.minFreqColorBox.setCurrentIndex(self.minFreqColorBox.findText(self.minFreqColor))
		self.layout.addWidget(self.minFreqColorBox, 5, 1)

		self.setLayout(self.layout)

	def initVar(self):
		self.cpuColor = self.Settings.value('CPU', 'yellow').toString()
		self.enableOnColor = self.Settings.value('EnableOn', 'red').toString()
		self.enableOffColor = self.Settings.value('EnableOff', 'blue').toString()
		self.governorColor = self.Settings.value('Governor', 'white').toString()
		self.maxFreqColor = self.Settings.value('MaxFreq', 'red').toString()
		self.minFreqColor = self.Settings.value('MinFreq', 'green').toString()

	def refreshInterfaceSettings(self):
		self.Settings.setValue('CPU', self.cpuColorBox.currentText())
		self.Settings.setValue('EnableOn', self.enableOnColorBox.currentText())
		self.Settings.setValue('EnableOff', self.enableOffColorBox.currentText())
		self.Settings.setValue('Governor', self.governorColorBox.currentText())
		self.Settings.setValue('MaxFreq', self.maxFreqColorBox.currentText())
		self.Settings.setValue('MinFreq', self.minFreqColorBox.currentText())
		self.Settings.sync()
		self.initVar()

	def eventClose(self, event):
		self.prnt.done(0)

def CreateApplet(parent):
	return plasmaCpuFreqUtility(parent)
