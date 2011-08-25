if (NOT CMAKE_INSTALL_PREFIX) 
 set (CMAKE_INSTALL_PREFIX /usr/local) 
endif ()

project (kde-plasma-cpufrequtility)

find_package(KDE4 REQUIRED)
find_package(PyKDE4 REQUIRED)
find_package(PyQt4 REQUIRED)

include (KDE4Defaults)
include_directories(${KDE4_INCLUDES})

set(cpu_freq_helper_SRCS contents/code/cpu_freq_helper.cpp)
set(CFH_PYTHON_SOURCES contents/code/main.py)
set(CFH_DESKTOP_FILE ${PROJECT_NAME}.desktop)
set(CFH_ICONS contents/icons/conservative.png
	      contents/icons/ondemand.png
	      contents/icons/performance.png
	      contents/icons/powersave.png)
set(IKDE4_DATA_DIR share/kde4)
set(IKDE4_APP_DIR ${IKDE4_DATA_DIR}/apps)
set(IKDE4_SERVICE_DIR ${IKDE4_DATA_DIR}/services)
set(IKDE4_PLASMOID_DIR ${IKDE4_APP_DIR}/plasma/plasmoids/${PROJECT_NAME})
if (${CMAKE_INSTALL_PREFIX} STREQUAL /usr)
 set(IKDE4_LIBEXEC_DIR libexec/kde4)
else ()
 set(IKDE4_LIBEXEC_DIR /usr/libexec/kde4)
endif ()

kde4_add_executable(cpu_freq_helper ${cpu_freq_helper_SRCS})
target_link_libraries(cpu_freq_helper ${KDE4_KDECORE_LIBS})

install(TARGETS cpu_freq_helper DESTINATION ${IKDE4_LIBEXEC_DIR})
kde4_install_auth_actions(org.freedesktop.auth.cpufrequtility contents/code/org.freedesktop.auth.cpufrequtility.actions)
kde4_install_auth_helper_files(cpu_freq_helper org.freedesktop.auth.cpufrequtility root)

file(READ metadata.desktop DESKTOP_FILE)
file(WRITE ${CFH_DESKTOP_FILE} ${DESKTOP_FILE})

#add_dependencies(cpu_freq_helper desktop_file)
install(FILES metadata.desktop DESTINATION ${IKDE4_PLASMOID_DIR})
install(FILES ${CFH_DESKTOP_FILE} DESTINATION ${IKDE4_SERVICE_DIR})
install(FILES ${CFH_PYTHON_SOURCES} DESTINATION ${IKDE4_PLASMOID_DIR}/contents/code)
install(FILES ${CFH_ICONS} DESTINATION ${IKDE4_PLASMOID_DIR}/contents/icons)
