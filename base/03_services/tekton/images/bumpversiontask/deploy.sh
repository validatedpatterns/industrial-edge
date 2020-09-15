oc new-build --strategy docker --binary --name=bumpversiontask

oc start-build bumpversiontask --from-file ./Dockerfile  --follow
