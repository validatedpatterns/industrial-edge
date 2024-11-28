#!/bin/sh -x

while [ 1 ]; do
	echo "Waiting for seed resources to be ready in manuela-ci"
	oc get -n manuela-ci pipeline seed 1>/dev/null 2>/dev/null && \
	oc get -n manuela-ci secret gitea-admin-secret 1>/dev/null 2>/dev/null && \
	echo "Bootstrap seed now can run" && break;
	sleep 5;
done

exit 0

