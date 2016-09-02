#!/bin/bash

# Run CoreCLR OSS tests on Linux (or Mac?)
# Use the instructions here:
#    https://github.com/dotnet/coreclr/blob/master/Documentation/building/unix-test-instructions.md
#
# Summary:
# 1. build coreclr and corefx on Linux.
# 2. build Linux mscorlib on Windows: build.cmd linuxmscorlib
# 3. copy tests to Linux:
#       cp --recursive /media/coreclr/bin/tests/Windows_NT.x64.Debug ~/test/
# 4. build product on Linux
# 5. Mount Windows shares on Linux
# 6. Run this script

CORECLRROOT=~/src/ManagedCodeGen
COREFXROOT=~/src/corefx
WINDOWSCORECLRROOT=~/brucefo1/ManagedCodeGen
TESTROOT=~/test

ARGS="\
--testRootDir=${TESTROOT}/Windows_NT.x64.Debug \
--testNativeBinDir=${CORECLRROOT}/bin/obj/Linux.x64.Debug/tests \
--coreClrBinDir=${CORECLRROOT}/bin/Product/Linux.x64.Debug \
--mscorlibDir=${WINDOWSCORECLRROOT}/bin/Product/Linux.x64.Debug \
--coreFxBinDir=${COREFXROOT}/bin/Linux.AnyCPU.Debug \
--coreFxNativeBinDir=${COREFXROOT}/bin/Linux.x64.Debug"

pushd ${CORECLRROOT}
echo ${CORECLRROOT}/tests/runtest.sh ${ARGS}
${CORECLRROOT}/tests/runtest.sh ${ARGS}
popd
