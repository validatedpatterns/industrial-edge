#!/bin/bash
target=$1
name=$(echo $1 | sed -e s@/@-@g -e s@charts-@@)
TEST_VARIANT="$2"
CHART_OPTS="$3"

TESTDIR=tests
#REFERENCE=${TESTDIR}/${name}-${TEST_VARIANT}.expected.yaml
#OUTPUT=${TESTDIR}/.${name}-${TEST_VARIANT}.expected.yaml
REFERENCE=${TESTDIR}/${name}.expected.yaml
OUTPUT=${TESTDIR}/.${name}.expected.yaml

echo "Testing $1 chart (${TEST_VARIANT})" >&2
helm template $target --name-template $name ${CHART_OPTS} > ${OUTPUT}
#cp ${OUTPUT} ${REFERENCE}
touch ${REFERENCE}
diff -u ${REFERENCE}  ${OUTPUT}
rc=$?
if [ $rc = 0 ]; then
    rm -f ${OUTPUT}
fi
exit $rc
