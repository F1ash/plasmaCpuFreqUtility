#include <kauth.h>
using namespace KAuth;
#include <iostream>
#include <QtGui>

class CPUFreqHelper : public QObject
{
	Q_OBJECT
	public:
		explicit CPUFreqHelper(QObject *parent = 0);

	public slots:
		ActionReply read(QVariantMap args);
		ActionReply write(QVariantMap args);
};
