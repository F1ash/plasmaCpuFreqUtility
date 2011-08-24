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

%build
make %{?_smp_mflags}

%install
make install DESTDIR=$RPM_BUILD_ROOT/usr

%files
%defattr(-,root,root)
%{_datadir}/kde4/services/%{name}.desktop
%{_datadir}/kde4/apps/plasma/plasmoids/%{name}/*
%dir %{_datadir}/kde4/apps/plasma/plasmoids/%{name}
%{_sysconfdir}/dbus-1/system.d/org.freedesktop.auth.cpufrequtility.conf
%{_prefix}/local/org.freedesktop.auth.cpufrequtility.conf
%{_prefix}/local/lib64/kde4/libexec/cpu_freq_helper
%{_prefix}/local/share/dbus-1/system-services/org.freedesktop.auth.cpufrequtility.service
%{_prefix}/share/polkit-1/actions/org.freedesktop.auth.cpufrequtility.policy

%clean
rm -rf $RPM_BUILD_ROOT

%changelog

* Mon Aug 22 2011 Fl@sh <kaperang07@gmail.com> - 1.2-1
- Initial build
