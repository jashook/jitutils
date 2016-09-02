@echo off
setlocal

REM Do a .NET Core SuperPMI collection across all tests in the coreclr repo.

REM Set the repo root.
set _root=d:\gh\ManagedCodeGen
if not exist %_root% echo Error: %_root% not found&goto :eof

REM Where to put the resulting MCH file?
set _mch=%_root%\bin\tests\alltests_win.mch

set _testbuild=%_root%\bin\tests\Windows_NT.x64.Debug
if not exist %_testbuild% echo Error: %_testbuild% not found&goto :eof
if not exist %_testbuild%\JIT\superpmi\superpmicollect\superpmicollect.exe echo Error: superpmicollect.exe not found&goto :eof

set _collect_script=%_root%\tests\src\JIT\superpmi\collect_runtest.cmd
if not exist %_collect_script% echo Error: %_collect_script% not found&goto :eof

if not exist %_root%\tests\runtest.cmd echo Error: %_root%\tests\runtest.cmd not found&goto :eof

REM Assume the default CORE_ROOT
if defined CORE_ROOT goto got_CORE_ROOT
set CORE_ROOT=%_testbuild%\Tests\Core_Root

set _prodbuild=%_root%\bin\Product\Windows_NT.x64.Debug
if not exist %_prodbuild% echo Error: %_prodbuild% not found&goto :eof
if not exist %_prodbuild%\coreclr.dll echo Error: %_prodbuild%\coreclr.dll not found&goto :eof

echo Using default CORE_ROOT as %CORE_ROOT%; copying built binaries from %__BinDir% to %CORE_ROOT%
if exist "%CORE_ROOT%" rd /s /q "%CORE_ROOT%"
md "%CORE_ROOT%"
xcopy /s "%_prodbuild%" "%CORE_ROOT%"

:got_CORE_ROOT
if not exist %CORE_ROOT% echo Error: CORE_ROOT (%CORE_ROOT%) not found&goto :eof
if not exist %CORE_ROOT%\coreclr.dll echo Error: coreclr.dll (%CORE_ROOT%\coreclr.dll) not found&goto :eof
if not exist %CORE_ROOT%\corerun.exe echo Error: corerun.exe (%CORE_ROOT%\corerun.exe) not found&goto :eof

REM Do the collection!
pushd %_testbuild%
%core_root%\corerun.exe %_testbuild%\JIT\superpmi\superpmicollect\superpmicollect.exe -mch %_mch% -run %_collect_script% %_root%\tests\runtest.cmd
popd
