; Salah Times Installer
Unicode True

!define APP_NAME "Salah Times"
!define APP_VERSION "2.0"
!define APP_PUBLISHER "Islamic Apps"
!define APP_EXE "SalahTimes.exe"
!define INSTALL_DIR "$PROGRAMFILES64\${APP_NAME}"
!define REG_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"

Name "${APP_NAME} ${APP_VERSION}"
OutFile "${BASEDIR}\SalahTimes-Setup.exe"
InstallDir "${INSTALL_DIR}"
InstallDirRegKey HKLM "${REG_KEY}" "InstallLocation"
RequestExecutionLevel admin
SetCompressor /SOLID lzma
BrandingText "${APP_PUBLISHER}"

!include "MUI2.nsh"

!define MUI_ICON "${BASEDIR}\installer\salah_times.ico"
!define MUI_UNICON "${BASEDIR}\installer\salah_times.ico"
!define MUI_ABORTWARNING
!define MUI_WELCOMEPAGE_TITLE "Welcome to ${APP_NAME} ${APP_VERSION} Setup"
!define MUI_WELCOMEPAGE_TEXT "This wizard will install ${APP_NAME} on your computer.$\r$\n$\r$\nPrayer times for 43 Moroccan cities with 3 language support.$\r$\n$\r$\nClick Next to continue."

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!define MUI_FINISHPAGE_RUN "$INSTDIR\${APP_EXE}"
!define MUI_FINISHPAGE_RUN_TEXT "Launch ${APP_NAME}"
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"

Section "Install"
    SetOutPath "$INSTDIR"

    File "${BASEDIR}\dist\SalahTimes.exe"
    File "${BASEDIR}\installer\salah_times.ico"

    CreateDirectory "$SMPROGRAMS\${APP_NAME}"
    CreateShortcut "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}" "" "$INSTDIR\salah_times.ico"
    CreateShortcut "$SMPROGRAMS\${APP_NAME}\Uninstall.lnk" "$INSTDIR\Uninstall.exe"
    CreateShortcut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}" "" "$INSTDIR\salah_times.ico"

    WriteUninstaller "$INSTDIR\Uninstall.exe"

    WriteRegStr HKLM "${REG_KEY}" "DisplayName" "${APP_NAME}"
    WriteRegStr HKLM "${REG_KEY}" "DisplayVersion" "${APP_VERSION}"
    WriteRegStr HKLM "${REG_KEY}" "Publisher" "${APP_PUBLISHER}"
    WriteRegStr HKLM "${REG_KEY}" "InstallLocation" "$INSTDIR"
    WriteRegStr HKLM "${REG_KEY}" "UninstallString" "$INSTDIR\Uninstall.exe"
    WriteRegStr HKLM "${REG_KEY}" "DisplayIcon" "$INSTDIR\salah_times.ico"
    WriteRegDWORD HKLM "${REG_KEY}" "NoModify" 1
    WriteRegDWORD HKLM "${REG_KEY}" "NoRepair" 1
SectionEnd

Section "Uninstall"
    Delete "$INSTDIR\${APP_EXE}"
    Delete "$INSTDIR\salah_times.ico"
    Delete "$INSTDIR\Uninstall.exe"
    RMDir "$INSTDIR"

    Delete "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk"
    Delete "$SMPROGRAMS\${APP_NAME}\Uninstall.lnk"
    RMDir "$SMPROGRAMS\${APP_NAME}"
    Delete "$DESKTOP\${APP_NAME}.lnk"

    DeleteRegKey HKLM "${REG_KEY}"
SectionEnd
