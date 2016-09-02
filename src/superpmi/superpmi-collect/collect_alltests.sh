#!/bin/bash

CORECLRROOT=~/src/ManagedCodeGen
TESTROOT=~/test
MCHFILE=${TESTROOT}/alltests_linux.mch

pushd ${TESTROOT}/Windows_NT.x64.Debug/JIT/superpmi/superpmicollect
${TESTROOT}/Windows_NT.x64.Debug/Tests/coreoverlay/corerun ${TESTROOT}/Windows_NT.x64.Debug/JIT/superpmi/superpmicollect/superpmicollect.exe -mch ${MCHFILE} -run ${CORECLRROOT}/tests/src/JIT/superpmi/runtests.sh
popd
