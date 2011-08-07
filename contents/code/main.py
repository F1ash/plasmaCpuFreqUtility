# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyKDE4.kdeui import KComboBox, KIcon, KMenu
from PyKDE4.kdecore import KUrl, KAuth, KGlobal
from PyKDE4.plasma import Plasma
from PyKDE4 import plasmascript
import os.path, os


COUNT_PROC = os.sysconf('SC_NPROCESSORS_ONLN')

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
"""

def define_proc_data():
	procData = {}
	procData['count'] = COUNT_PROC
	procData['availableFreqs'] = {i : readCpuData(str(i), 'available_frequencies') for i in xrange(COUNT_PROC)}
	#print [procData['availableFreqs'][i].data()[QString('contents')].toString() for i in xrange(COUNT_PROC)]
	procData['availableGovernors'] = {i : readCpuData(str(i), 'available_governors') for i in xrange(COUNT_PROC)}
	#print [procData['availableGovernors'][i].data()[QString('contents')].toString() for i in xrange(COUNT_PROC)]
	procData['currentFreq'] = {i : readCpuData(str(i), 'cur_freq') for i in xrange(COUNT_PROC)}
	#print [procData['currentFreq'][i].data()[QString('contents')].toString() for i in xrange(COUNT_PROC)]
	procData['currentGovernor'] = {i : readCpuData(str(i), 'governor') for i in xrange(COUNT_PROC)}
	#print [procData['currentGovernor'][i].data()[QString('contents')].toString() for i in xrange(COUNT_PROC)]
	procData['currentMaxFreq'] = {i : readCpuData(str(i), 'max_freq') for i in xrange(COUNT_PROC)}
	#print [procData['currentMaxFreq'][i].data()[QString('contents')].toString() for i in xrange(COUNT_PROC)]
	procData['currentMinFreq'] = {i : readCpuData(str(i), 'min_freq') for i in xrange(COUNT_PROC)}
	#print [procData['currentMinFreq'][i].data()[QString('contents')].toString() for i in xrange(COUNT_PROC)]
	return procData

class plasmaCpuFreqUtility(plasmascript.Applet):
	def __init__(self, parent = None):
		plasmascript.Applet.__init__(self, parent)

		self.kdehome = unicode(KGlobal.dirs().localkdedir())
		#self.iconPath = os.path.join(self.kdehome, '/share/apps/plasma/plasmoids/plasmaCpuFreqUtility/contents/icons/icon.svg')
		self.iconPath = '../icons/icon.svg'
		self.icon = Plasma.IconWidget()
		self.icon.setIcon(self.iconPath)
		self.icon.clicked.connect(self.mouseDoubleClickEvent)
		#if not os.path.isfile(os.path.expanduser('~/.actions')) : createActions()
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

class ControlWidget(Plasma.Dialog):
	def __init__(self, procData, obj, parent = None):
		Plasma.Dialog.__init__(self, parent)
		self.prnt = obj
		self.ProcData = procData

		self.accept = QPushButton()
		self.accept.setText('Apply')
		self.accept.clicked.connect(self.changeRegime)
		#self.accept.setMaximumHeight(20)
		self.reset = QPushButton()
		self.reset.setText("Reset")
		self.reset.clicked.connect(self.regimeDefined)
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
			if i == 0 :
				self.cpuEnable[i].setCheckState(Qt.Checked)
				self.cpuEnable[i].setEnabled(False)
			else :
				self.cpuEnable[i].setCheckState(Qt.Checked)
			self.layout.addWidget(self.cpuEnable[i], 1 + i, 1)

			self.comboGovernorMenu[i] = QComboBox(self)
			_availableGovernors = self.ProcData['availableGovernors'][i].data()[QString('contents')].toString().replace('\n', '')
			availableGovernors = _availableGovernors.split(' ')
			count = availableGovernors.count('')
			if count > 0 : availableGovernors.removeAll('')
			for governor in availableGovernors :
				self.comboGovernorMenu[i].addItem(QIcon('../icons/' + governor + '.png'), governor)
			currentGovernor = self.ProcData['currentGovernor'][i].data()[QString('contents')].toString().replace('\n', '')
			currGovernorIdx = availableGovernors.indexOf(currentGovernor)
			#print [currentGovernor], currGovernorIdx, [item for item in availableGovernors]
			self.comboGovernorMenu[i].setCurrentIndex(currGovernorIdx)
			self.comboGovernorMenu[i].setEditable(False)
			#self.comboGovernorMenu[i].currentIndexChanged['const QString&'].connect(self.regimeDefined)
			self.layout.addWidget(self.comboGovernorMenu[i], 1 + i, 2)

			self.comboMinFreq[i] = QComboBox(self)
			_availableFreqs = self.ProcData['availableFreqs'][i].data()[QString('contents')].toString().replace('\n', '')
			availableFreqs = _availableFreqs.split(' ')
			count = availableFreqs.count('')
			if count > 0 : availableFreqs.removeAll('')
			for j in availableFreqs :
				self.comboMinFreq[i].addItem(str(j)[:-3])
			currentMinFreq = self.ProcData['currentMinFreq'][i].data()[QString('contents')].toString().replace('\n', '')
			currMinFreqIdx = availableFreqs.indexOf(currentMinFreq)
			self.comboMinFreq[i].setCurrentIndex(currMinFreqIdx)
			self.layout.addWidget(self.comboMinFreq[i], 1 + i, 3)

			self.comboMaxFreq[i] = QComboBox(self)
			_availableFreqs = self.ProcData['availableFreqs'][i].data()[QString('contents')].toString().replace('\n', '')
			availableFreqs = _availableFreqs.split(' ')
			count = availableFreqs.count('')
			if count > 0 : availableFreqs.removeAll('')
			for j in availableFreqs :
				self.comboMaxFreq[i].addItem(str(j)[:-3])
			currentMaxFreq = self.ProcData['currentMaxFreq'][i].data()[QString('contents')].toString().replace('\n', '')
			currMaxFreqIdx = availableFreqs.indexOf(currentMaxFreq)
			self.comboMaxFreq[i].setCurrentIndex(currMaxFreqIdx)
			self.layout.addWidget(self.comboMaxFreq[i], 1 + i, 4)

		self.setLayout(self.layout)

	def regimeDefined(self, str_ = ''):
		print str_, '==='
		if str_ == 'Performance' :
			self.changeRegime('performance')
		elif str_ == 'OnDemand' :
			self.changeRegime('ondemand')
		elif str_ == 'Conservative' :
			self.changeRegime('conservative')
		elif str_== 'PowerSave' :
			self.changeRegime('powersave')

	def changeRegime(self, key = None):
		args = {}
		args['key'] = key
		act = KAuth.Action()

		act.setName('org.freedesktop.auth.cpufrequtility.write')
		act.setHelperID('org.freedesktop.auth.cpufrequtility')
		act.setArguments(args)
		print act.status()
		reply = act.execute()
		if (reply.failed()) :
			QMessageBox.information(self, "Error",
					QString("KAuth returned an error code: %1 \n %2").arg(reply.errorCode()).arg(reply.errorDescription()))
		else :
			print reply.data(), 'reply'

def CreateApplet(parent):
	return plasmaCpuFreqUtility(parent)
