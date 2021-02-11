#!/bin/bash

ENDPOINT=$1
RSE=$2
FILE=$3

FTS_SERVER="https://fts3-cms.cern.ch:8446" 


echo "Testing: "$ENDPOINT

# Test I can write to endpoint
echo "Checking I can write to $ENDPOINT/store/temp/user/ddavila/$FILE" 
gfal-copy -f -p $(pwd)/$FILE $ENDPOINT/store/temp/user/ddavila/$FILE

if [ $? -eq 0 ]; then
    echo gfal-copy: OK
else
    echo: gfal-copy: FAILED
    exit
fi


# Test FTS TPC Endpoint as Source
TPC_SOURCE="$ENDPOINT/store/temp/user/ddavila/$FILE"
TPC_DEST="davs://redirector.t2.ucsd.edu:1094/store/user/ddavila/TPC/$RSE/$FILE"

TRANSFER_ID=$(fts-transfer-submit -o --compare-checksums -s $FTS_SERVER $TPC_SOURCE $TPC_DEST) 
echo "TRANSFER ID: "$TRANSFER_ID

RESULT=$(fts-transfer-status -s $FTS_SERVER $TRANSFER_ID)
while [ $RESULT != "FINISHED" ] && [ $RESULT != "FAILED" ]
do
  echo "RESULT: $RESULT"
  sleep 5
  RESULT=$(fts-transfer-status -s $FTS_SERVER $TRANSFER_ID)
done

if [ $RESULT == "FINISHED" ]
then
  echo fts-transfer-submit endpoint as source: OK
else [ $RESULT == "FAILED" ]
  echo fts-transfer-submit endpoint as source: FAILED
  exit
fi


# Test FTS TPC Endpoint as Destination
TPC_SOURCE="davs://redirector.t2.ucsd.edu:1094/store/user/ddavila/TPC/$RSE/$FILE"
TPC_DEST="$ENDPOINT/store/temp/user/ddavila/TPC_WRITE/$FILE"

TRANSFER_ID=$(fts-transfer-submit -o --compare-checksums -s $FTS_SERVER $TPC_SOURCE $TPC_DEST)
echo "TRANSFER ID: "$TRANSFER_ID

RESULT=$(fts-transfer-status -s $FTS_SERVER $TRANSFER_ID)
while [ $RESULT != "FINISHED" ] && [ $RESULT != "FAILED" ]
do
  echo "RESULT: $RESULT"
  sleep 5
  RESULT=$(fts-transfer-status -s $FTS_SERVER $TRANSFER_ID)
done

if [ $RESULT == "FINISHED" ]
then
  echo fts-transfer-submit endpoint as destination: OK
else [ $RESULT == "FAILED" ]
  echo fts-transfer-submit endpoint as destination: FAILED
  exit
fi
 
