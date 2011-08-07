# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyKDE4.kdeui import KComboBox, KIcon, KMenu
from PyKDE4.kdecore import KUrl, KAuth, KGlobal
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
	count = readCpuData('', 'possible').data()[QString('contents')].toString().replace('\n', '').split('-')
	present = readCpuData('', 'present').data()[QString('contents')].toString().replace('\n', '').split('-')
	#print len(count), COUNT_PROCESSOR, ":", [str(present[i]) for i in xrange(len(present))]
	global COUNT_PROC
	COUNT_PROC = max(COUNT_PROCESSOR, len(count))
	procData['count'] = COUNT_PROC
	procData['availableFreqs'] = {int(i) : readCpuData(str(i), 'available_frequencies') for i in present}
	#print [procData['availableFreqs'][i].data()[QString('contents')].toString() for i in xrange(COUNT_PROC)]
	procData['availableGovernors'] = {int(i) : readCpuData(str(i), 'available_governors') for i in present}
	#print [procData['availableGovernors'][i].data()[QString('contents')].toString() for i in xrange(COUNT_PROC)]
	procData['currentFreq'] = {int(i) : readCpuData(str(i), 'cur_freq') for i in present}
	#print [procData['currentFreq'][i].data()[QString('contents')].toString() for i in xrange(COUNT_PROC)]
	procData['currentGovernor'] = {int(i) : readCpuData(str(i), 'governor') for i in present}
	#print [procData['currentGovernor'][i].data()[QString('contents')].toString() for i in xrange(COUNT_PROC)]
	procData['currentMaxFreq'] = {int(i) : readCpuData(str(i), 'max_freq') for i in present}
	#print [procData['currentMaxFreq'][i].data()[QString('contents')].toString() for i in xrange(COUNT_PROC)]
	procData['currentMinFreq'] = {int(i) : readCpuData(str(i), 'min_freq') for i in present}
	#print [procData['currentMinFreq'][i].data()[QString('contents')].toString() for i in xrange(COUNT_PROC)]
	""" WARNING : /sys/devices/system/cpu/cpu0/online not exist anyway """
	present.removeAll('0')
	procData['online'] = {int(i) : readCpuData(str(i), 'online') for i in present}
	#print [procData['online'][i].data()[QString('contents')].toString() for i in xrange(COUNT_PROC)]
	return procData

class plasmaCpuFreqUtility(plasmascript.Applet):
	def __init__(self, parent = None):
		plasmascript.Applet.__init__(self, parent)

		self.kdehome = unicode(KGlobal.dirs().localkdedir())
		self.iconPath = self.kdehome + 'share/apps/plasma/plasmoids/plasmaCpuFreqUtility/contents/icons/icon.svg'
		
		self.icon = Plasma.IconWidget()
		self.icon.setIcon(self.iconPath)
		self.icon.clicked.connect(self.mouseDoubleClickEvent)
		self.ProcData = define_proc_data()

	def init(self):
		self.setImmutability(Plasma.Mutable)
		self.layout = QGraphicsLinearLayout(self.applet)
		self.layout.setSpacing(0)
		self.Control = ControlWidget(self.ProcData, self)

		self.layout.addItem(self.icon)

		self.setLayout(self.layout)

		Plasma.ToolTipManager.self().setContent( self.applet, Plasma.ToolTipContent( \
								'CPU FreqUtility', \
								QString(''), self.icon.icon() ) )

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
		self.Control = ControlWidget(self.ProcData, self)
		self.mouseDoubleClickEvent()

class ControlWidget(Plasma.Dialog):
	def __init__(self, procData, obj, parent = None):
		Plasma.Dialog.__init__(self, parent)
		self.prnt = obj
		self.ProcData = procData
		self.kdehome = unicode(KGlobal.dirs().localkdedir())

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

		self.layout = QGridLayout()
		self.layout.setSpacing(0)
		self.layout.addItem(self.buttonPanel, 0, 2)
		self.minLabel = QLabel('<font color=green>MinFreq</font>')
		self.maxLabel = QLabel('<font color=red>MaxFreq</font>')
		self.layout.addWidget(self.minLabel, 0, 3, Qt.AlignCenter)
		self.layout.addWidget(self.maxLabel, 0, 4, Qt.AlignCenter)

		self.cpuLabel = {}
		self.cpuEnable = {}
		self.comboGovernorMenu = {}
		self.comboMinFreq = {}
		self.comboMaxFreq = {}
		for i in xrange(COUNT_PROC) :
			self.cpuLabel[i] = QLabel('<font color=yellow>CPU' + str(i) + '</font>')
			self.layout.addWidget(self.cpuLabel[i], 1 + i, 0)

			self.cpuEnable[i] = QCheckBox()
			if i != 0 :
				enabled = int(self.ProcData['online'][i].data()[QString('contents')].toString().replace('\n', ''))
				#print enabled
			if i == 0 :
				self.cpuEnable[i].setCheckState(Qt.Checked)
				self.cpuEnable[i].setEnabled(False)
			else :
				if enabled == 1 :
					self.cpuEnable[i].setCheckState(Qt.Checked)
				if enabled == 0 :
					self.cpuEnable[i].setCheckState(Qt.Unchecked)
			self.layout.addWidget(self.cpuEnable[i], 1 + i, 1)

			self.comboGovernorMenu[i] = QComboBox(self)
			_availableGovernors = self.ProcData['availableGovernors'][i].data()[QString('contents')].toString().replace('\n', '')
			availableGovernors = _availableGovernors.split(' ')
			count = availableGovernors.count('')
			if count > 0 : availableGovernors.removeAll('')
			availableGovernors.append('powersave')
			availableGovernors.append('conservative')
			availableGovernors.removeDuplicates()
			for governor in availableGovernors :
				iconPath = self.kdehome + 'share/apps/plasma/plasmoids/plasmaCpuFreqUtility/contents/icons/'
				if os.path.isfile(iconPath + governor + '.png') :
					path_ = iconPath + governor + '.png'
				else :
					path_ = iconPath + 'conservative.png'
				self.comboGovernorMenu[i].addItem(QIcon(), governor)
			currentGovernor = self.ProcData['currentGovernor'][i].data()[QString('contents')].toString().replace('\n', '')
			currGovernorIdx = availableGovernors.indexOf(currentGovernor)
			#print [currentGovernor], currGovernorIdx, [item for item in availableGovernors]
			self.comboGovernorMenu[i].setCurrentIndex(currGovernorIdx)
			self.comboGovernorMenu[i].setEditable(False)
			#self.comboGovernorMenu[i].currentIndexChanged['const QString&'].connect(self.regimeDefined)
			self.layout.addWidget(self.comboGovernorMenu[i], 1 + i, 2)

			self.comboMinFreq[i] = QComboBox(self)
			#self.comboMinFreq[i].setMinimumContentsLength(8)
			_availableFreqs = self.ProcData['availableFreqs'][i].data()[QString('contents')].toString().replace('\n', '')
			availableFreqs = _availableFreqs.split(' ')
			count = availableFreqs.count('')
			if count > 0 : availableFreqs.removeAll('')
			for j in availableFreqs :
				if j == 'default' : continue
				self.comboMinFreq[i].addItem(str(j)[:-3])
			self.comboMinFreq[i].addItem('default')
			currentMinFreq = self.ProcData['currentMinFreq'][i].data()[QString('contents')].toString().replace('\n', '')
			currMinFreqIdx = availableFreqs.indexOf(currentMinFreq)
			self.comboMinFreq[i].setCurrentIndex(currMinFreqIdx)
			self.layout.addWidget(self.comboMinFreq[i], 1 + i, 3)

			self.comboMaxFreq[i] = QComboBox(self)
			#self.comboMaxFreq[i].setMinimumContentsLength(8)
			_availableFreqs = self.ProcData['availableFreqs'][i].data()[QString('contents')].toString().replace('\n', '')
			availableFreqs = _availableFreqs.split(' ')
			count = availableFreqs.count('')
			if count > 0 : availableFreqs.removeAll('')
			for j in availableFreqs :
				if j == 'default' : continue
				self.comboMaxFreq[i].addItem(str(j)[:-3])
			self.comboMaxFreq[i].addItem('default')
			currentMaxFreq = self.ProcData['currentMaxFreq'][i].data()[QString('contents')].toString().replace('\n', '')
			currMaxFreqIdx = availableFreqs.indexOf(currentMaxFreq)
			self.comboMaxFreq[i].setCurrentIndex(currMaxFreqIdx)
			self.layout.addWidget(self.comboMaxFreq[i], 1 + i, 4)

		self.setLayout(self.layout)

	def getNewProcParemeters(self):
		newParameters = {}
		for i in xrange(COUNT_PROC) :

			newParameters[i] = {}
			""" WARNING : /sys/devices/system/cpu/cpu0/online not exist anyway """
			if i != 0 : newParameters[i]['enable'] = int(self.cpuEnable[i].checkState())/2
			newParameters[i]['regime'] = self.comboGovernorMenu[i].currentText()
			value = self.comboMinFreq[i].currentText()
			if value != 'default' : value += '000'
			newParameters[i]['minfrq'] = value
			value = self.comboMaxFreq[i].currentText()
			if value != 'default' : value += '000'
			newParameters[i]['maxfrq'] = value

		return newParameters

	def changeRegime(self, key = None):
		newParameters = self.getNewProcParemeters()
		for i in xrange(COUNT_PROC) :
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
		self.prnt.parametersReset()

def CreateApplet(parent):
	return plasmaCpuFreqUtility(parent)
