#!/bin/bash

JOB_NAME=$1
BUILD_NUMBER=$2
BUILD_URL=$3
UPSTREAM_BUILD_URL=$4

#JENKINS_URL="http://192.168.0.33:8080/view/QA/job"
#UP_STREAM_PROJECT="http://192.168.0.33:8080/job/BeMail_Android"
#PROJECT="BMAM_Android"
#BUILD_NUMBER="51"
#COM="bmca"
#line=$(curl http://10.0.11.0:8082/view/QA/job/APITest/$BUILD_NUMBER/consoleText)
line=$(curl $BUILD_URL/consoleText)
strA="Started by upstream project"
strB="Started by timer"
strC="Started by user"
jobType=""

if [[ "$line" =~ "$strA" ]]
then
    jobType="Buildly"
#	split=`echo $line|cut -d " " -f8`
#    buildly_number=$split
else
    if [[ "$line" =~ "$strB" ]]
    then jobType="Nightly"
    else
        if [[ "$line" =~ "$strC" ]]
        then
            if [[ "$UPSTREAM_BUILD_URL" == "" ]]
            then jobType="Manually"
            else
               jobType="Buildly"
            fi
        fi
    fi
fi

if [[ "$JOB_NAME" == "TASKS" ]]
then
    COMPONENT="tasks"
else
    if [[ "$JOB_NAME" == "MODULE_UPDATE" ]]
    then COMPONENT="module_update"
    else
        if [[ "$JOB_NAME" == "PERFORMANCE" ]]
        then COMPONENT="performance"
        fi
     fi
fi


jobid=$JOB_NAME$BUILD_NUMBER
echo $jobid
jobinfo="$jobid $jobType $COMPONENT $BUILD_NUMBER $UPSTREAM_BUILD_URL"
echo $jobinfo

./rssh.sh 10.0.10.211 root vlifeqa "echo $jobinfo >>jenkinsjob.txt"
./rssh.sh 10.0.10.211 root vlifeqa "python AutoTestFrame/controller/jenkins_job/queryjob.py $jobid"
./rscp.sh 10.0.10.211 root vlifeqa "result.txt" "."
if [ ! -f "result.txt" ]
then echo "Job is FAILED"
else
    cat result.txt | while read myline
    do
     echo "Job is "$myline
    done
fi


if [[ ! -d "/tmp/$JOB_NAME" ]]
then mkdir "/tmp/$JOB_NAME"
fi

if [[ ! -d "/tmp/$JOB_NAME/$BUILD_NUMBER" ]]
then mkdir "/tmp/$JOB_NAME/$BUILD_NUMBER"
fi
./rscp.sh 10.0.11.72 root vlife!1 /mnt/rflog/$COMPONENT/$jobid/output.xml  /tmp/$JOB_NAME/$BUILD_NUMBER/
./rscp.sh 10.0.11.72 root vlife!1 /mnt/rflog/$COMPONENT/$jobid/report.html  /tmp/$JOB_NAME/$BUILD_NUMBER/
./rscp.sh 10.0.11.72 root vlife!1 /mnt/rflog/$COMPONENT/$jobid/log.html  /tmp/$JOB_NAME/$BUILD_NUMBER/


