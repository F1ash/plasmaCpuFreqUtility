#include <QFile>
#include <QTextStream>
#include "cpu_freq_helper.h"


CPUFreqHelper::CPUFreqHelper(QObject *parent) : QObject(parent) {
}

ActionReply CPUFreqHelper::read(QVariantMap args)
{
	ActionReply reply;
 
	QFile fileOut("myLog");
	if (!fileOut.open(QIODevice::WriteOnly | QIODevice::Text)) {
		QVariantMap err;
		err["contents"] = QString("Done");
		reply.setData(err);
		/*QMessageBox::information(0, QString("Error"), QString("Creating Log Error"), 0, 0, 0);*/
		return reply;
	};
	QTextStream out(&fileOut);
	QString filename = args["filename"].toString();
	out << filename << endl;
	QString procnumb = args["procnumb"].toString();
	out << procnumb << endl;
	QFile file("/sys/devices/system/cpu/cpu" + procnumb + "/cpufreq/scaling_" + filename);
	out << "/sys/devices/system/cpu/cpu" + procnumb + "/cpufreq/scaling_" + filename << endl;
 
	if (!file.open(QIODevice::ReadOnly)) {
		reply = ActionReply::HelperErrorReply;
		reply.setErrorCode(file.error());
		QVariantMap err;
		err["contents"] = QString("Done");
		reply.setData(err);
		out << "Done" << endl;
		fileOut.close();
		return reply;
	};
 
	QTextStream stream(&file);
	QString contents = stream.readAll();
 
	QVariantMap retdata;
	retdata["contents"] = contents;
	out << contents << "Success" << endl;
 
	reply.setData(retdata);
	file.close();
	fileOut.close();
	return reply;
}

ActionReply CPUFreqHelper::write(QVariantMap args)
{
	ActionReply reply;
 
	QFile fileOut("/tmp/myLog");
	if (!fileOut.open(QIODevice::WriteOnly | QIODevice::Text)) {
		QVariantMap err;
		err["contents"] = QString("Done");
		reply.setData(err);
		return reply;
	};
	QTextStream outLog(&fileOut);
	QString filename = args["filename"].toString();
	QString procnumb = args["procnumb"].toString();
	QString parametr = args["parametr"].toString();
	QFile file("/sys/devices/system/cpu/cpu" + procnumb + "/cpufreq/scaling_" + filename);
 
	if (!file.open(QIODevice::WriteOnly)) {
		reply = ActionReply::HelperErrorReply;
		reply.setErrorCode(file.error());
 
		return reply;
	};
 
	QTextStream out(&file);
	out << parametr << endl;
	outLog << "/sys/devices/system/cpu/cpu" + procnumb + "/cpufreq/scaling_" + filename \
		   << parametr << endl;

	QVariantMap retdata;
	retdata["contents"] = QString("Success");
	reply.setData(retdata);
	out << "Success" << endl;
	file.close();
	fileOut.close();
	return reply;
}

KDE4_AUTH_HELPER_MAIN("org.freedesktop.auth.cpufrequtility", CPUFreqHelper)
