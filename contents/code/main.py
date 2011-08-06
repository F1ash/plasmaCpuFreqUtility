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
	args["procnumb"] = number
	args["filename"] = fileName

	act = KAuth.Action('org.freedesktop.auth.cpufrequtility.read')
	act.setHelperID('org.freedesktop.auth.cpufrequtility')
	act.setArguments(args)
	print act.hasHelper(), 'ready', act.helperID()
	#act.arguments()["procnumb"] = number
	#act.arguments()["filename"] = fileName
	reply = act.execute()
	if (reply.failed()) :
		QMessageBox.information(None, "Error", QString("KAuth returned an error code: %1").arg(reply.errorCode()))
	else :
		print reply.data(), 'reply from :', act.hasHelper(), act.name(), 'Valid is', act.isValid()
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
		QMessageBox.information(None, "Error", QString("KAuth returned an error code: %1").arg(reply.errorCode()))
	else :
		print reply.data(), 'reply from :', act.hasHelper(), act.name(), 'Valid is', act.isValid()
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
	print [procData['availableFreqs'][i].data() for i in xrange(COUNT_PROC)]
	procData['availableGovernors'] = {}
	procData['currentFreq'] = {}
	procData['currentGovernor'] = {}
	procData['currentMaxFreq'] = {}
	procData['currentMinFreq'] = {}
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

		self.comboMenu = KComboBox(False, self)
		self.comboMenu.addUrl(KIcon('../icons/performance.png'), KUrl('Performance'))
		self.comboMenu.addUrl(KIcon('../icons/ondemand.png'), KUrl('OnDemand'))
		self.comboMenu.addUrl(KIcon('../icons/ondemand.png'), KUrl('Conservative'))
		self.comboMenu.addUrl(KIcon('../icons/powersave.png'), KUrl('PowerSave'))
		self.comboMenu.setCurrentItem('OnDemand')
		self.comboMenu.setEditable(False)
		self.comboMenu.currentIndexChanged['const QString&'].connect(self.regimeDefined)

		self.layout = QGridLayout()
		self.layout.setSpacing(0)
		self.layout.addWidget(self.comboMenu, 0, 0)

		self.setLayout(self.layout)

	def regimeDefined(self, str_ = ''):
		print str_, '==='
		if str_ == 'Performance' :
			self.changeRegime('performance')
		elif str_ == 'OnDemand':
			self.changeRegime('ondemand')
		elif str_ == 'Conservative':
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
			QMessageBox.information(self, "Error", QString("KAuth returned an error code: %1").arg(reply.errorCode()))
		else :
			print reply.data(), 'reply'

class RegimeChange():
	def __init__(self, parent = None):
		pass

	def modechange(self, args):
		reply = KAuth.ActionReply()
		Data = QStringList()
		Data.append('echo')
		Data.append(args['key'])
		Data.append('>')
		Data.append('/sys/devices/system/cpu/cpu*/cpufreq/scaling_governor')
		self.proc = QProcess()
		start, pid = self.proc.startDetached('/usr/bin/pkexec', Data, os.getcwd())
		reply.setData({'pid' : pid, 'start' :start})
		return reply

	def define_proc_data(self, args):
		reply = KAuth.ActionReply()
		with open('/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor', 'rb') as f :
			mode = f.read()
		reply.setData({'mode' : mode})
		return reply

def CreateApplet(parent):
	return plasmaCpuFreqUtility(parent)
