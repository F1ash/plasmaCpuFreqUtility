Name: kde-plasma-cpufrequtility
Version: 1.2
Release: 1%{?dist}
Summary: CPU Frequence Utility plasmoid.
Summary(ru): Плазмоид для управления режимом работы процессора.
Group: Applications/Utility
License: GPL
Source0: http://cloud.github.com/downloads/F1ash/plasmaCpuFreqUtility/%{name}-%{version}.tar.bz2
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
URL: https://github.com/F1ash/plasmaCpuFreqUtility
BuildArch: x86_64

Requires: python, PyQt4, PyKDE4
BuildRequires: g++

%description
kde-plasma-cpufrequtility
CPU Frequence Utility plasmoid.

%description -l ru
kde-plasma-cpufrequtility
Плазмоид для управления режимом работы процессора.

%prep
%setup -q

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/%{_datadir}/kde4/apps/plasma/plasmoids/%{name}
cp -r * $RPM_BUILD_ROOT/%{_datadir}/kde4/apps/plasma/plasmoids/%{name}/
mkdir -p $RPM_BUILD_ROOT/%{_datadir}/kde4/services
cp -r metadata.desktop $RPM_BUILD_ROOT/%{_datadir}/kde4/services/%{name}.desktop
cp $RPM_BUILD_ROOT/usr/local/etc/dbus-1/system.d/org.freedesktop.auth.cpufrequtility.conf \
   %{_sysconfdir}/dbus-1/system.d/org.freedesktop.auth.cpufrequtility.conf

%files
%defattr(-,root,root)
%{_datadir}/kde4/services/%{name}.desktop
%{_datadir}/kde4/apps/plasma/plasmoids/%{name}/*
%{_sysconfdir}/dbus-1/system.d/org.freedesktop.auth.cpufrequtility.conf
%dir %{_datadir}/kde4/apps/plasma/plasmoids/%{name}

%clean
rm -rf $RPM_BUILD_ROOT

%changelog

* Mon Aug 22 2011 Fl@sh <kaperang07@gmail.com> - 1.2-1
- Initial build
