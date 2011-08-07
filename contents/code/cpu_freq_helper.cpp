#include <QFile>
#include <QTextStream>
#include "cpu_freq_helper.h"


CPUFreqHelper::CPUFreqHelper(QObject *parent) : QObject(parent) {
}

QString CPUFreqHelper::get_key_varmap(const QVariantMap &args, const QString& key)
{
	QString value;
	if (args.keys().contains(key)) {
		value = args[key].toString();
	}
	else {
		value = QString();
	};
	
	return value;
}

ActionReply CPUFreqHelper::read(QVariantMap args)
{
	ActionReply reply;
 
	QString filename = get_key_varmap(args, "filename");
	QString procnumb = get_key_varmap(args, "procnumb");
	if (filename.isEmpty() or procnumb.isEmpty()) {
		QVariantMap err;
		err["contents"] = QString("default");
		reply.setData(err);
		return reply;
	}
	QFile file;
	if (filename == "online") {
		file.setFileName("/sys/devices/system/cpu/cpu" + procnumb + "/" + filename);
	}
	else if (filename == "possible") {
		file.setFileName("/sys/devices/system/cpu/possible");
	}
	else if (filename == "present") {
		file.setFileName("/sys/devices/system/cpu/present");
	}
	else {
		file.setFileName("/sys/devices/system/cpu/cpu" + procnumb + "/cpufreq/scaling_" + filename);
	};
 
	if (!file.open(QIODevice::ReadOnly)) {
		QVariantMap err;
		err["contents"] = QString("default");
		reply.setData(err);
		return reply;
	};
 
	QTextStream stream(&file);
	QString contents = stream.readAll();
 
	QVariantMap retdata;
	retdata["contents"] = contents;
 
	reply.setData(retdata);
	file.close();
	return reply;
}

ActionReply CPUFreqHelper::write(QVariantMap args)
{
	ActionReply reply;

	QString filename = get_key_varmap(args, "filename");
	QString procnumb = get_key_varmap(args, "procnumb");
	QString parametr = get_key_varmap(args, "parametr");
	if (filename.isEmpty() or procnumb.isEmpty() or parametr.isEmpty()) {
		reply = ActionReply::HelperErrorReply;
		reply.setErrorCode(255);
		reply.setErrorDescription("Some data is not initialized.");
		return reply;
	}
	QFile file;
	if (filename != "online") {
		file.setFileName("/sys/devices/system/cpu/cpu" + procnumb + "/cpufreq/scaling_" + filename);
	}
	else {
		file.setFileName("/sys/devices/system/cpu/cpu" + procnumb + "/" + filename);
	};
 
	if (!file.open(QIODevice::WriteOnly)) {
		reply = ActionReply::HelperErrorReply;
		reply.setErrorCode(file.error());
 
		return reply;
	};
 
	QTextStream out(&file);
	out << parametr << endl;

	QVariantMap retdata;
	retdata["contents"] = QString("Success");
	reply.setData(retdata);
	file.close();
	return reply;
}

KDE4_AUTH_HELPER_MAIN("org.freedesktop.auth.cpufrequtility", CPUFreqHelper)
