DESTDIR=/usr
INSTALL=install -D -m 0644 -p
APP_NAME=kde-plasma-cpufrequtility
KAPPS=share/kde4/apps
KSERV=share/kde4/services
PLASMA=plasma/plasmoids
CODE=contents/code
ICONS=contents/icons
DBUS_SERV_NAME=org.freedesktop.auth.cpufrequtility
CONFIG=etc/dbus-1/system.d/$(DBUS_SERV_NAME).conf
ARCH=${arch=${HOSTTYPE:${#HOSTTYPE}-2}//86/}

contents/code/build:
	cd contents/code
	mkdir build
	cd build
	cmake ..
	make

build: contents/code/build
	@echo "Nothing to build"

install: build
	$(INSTALL) metadata.desktop $(DESTDIR)/$(KSERV)/$(APP_NAME).desktop
	$(INSTALL) $(CODE)/main.py $(DESTDIR)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(CODE)/main.py
	$(INSTALL) $(ICONS)/conservative.png $(DESTDIR)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(ICONS)/conservative.png
	$(INSTALL) $(ICONS)/ondemand.png $(DESTDIR)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(ICONS)/ondemand.png
	$(INSTALL) $(ICONS)/performance.png $(DESTDIR)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(ICONS)/performance.png
	$(INSTALL) $(ICONS)/powersave.png $(DESTDIR)/$(KAPPS)/$(PLASMA)/$(APP_NAME)/$(ICONS)/powersave.png
	$(INSTALL) $(DESTDIR)/local/$(CONFIG) $(CONFIG)

clean:
	rm -rf $(DESTDIR)/$(KSERV)/$(APP_NAME).desktop
	rm -rf $(DESTDIR)/$(KAPPS)/$(PLASMA)/$(APP_NAME)
	rm -rf /$(CONFIG)
	rm -rf $(DESTDIR)/local/$(CONFIG)
	rm -rf $(DESTDIR)/local/lib$(ARCH)/kde4/libexec/cpu_freq_helper
	rm -rf $(DESTDIR)/local/share/dbus-1/system-services/$(DBUS_SERV_NAME).service
	rm -rf $(DESTDIR)/share/polkit-1/actions/$(DBUS_SERV_NAME).policy
