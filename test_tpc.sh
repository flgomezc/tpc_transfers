#!/bin/bash
USER=fgomezco
FTS_SERVER="https://fts3-cms.cern.ch:8446"

ENDPOINT=$1
RSE=$2
FILE=$3

function transfer {
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
}

echo "Testing: "$ENDPOINT

# Test I can write to endpoint
echo "Checking I can write to $ENDPOINT/store/temp/user/$USER/$FILE" 
gfal-copy -f -p $(pwd)/$FILE $ENDPOINT/store/temp/user/$USER/$FILE

if [ $? -eq 0 ]; then
    echo gfal-copy: OK
else
    echo gfal-copy: FAILED
    exit
fi



# Test FTS TPC Endpoint as Source
echo "Testing $ENDPOINT as source"
TPC_SOURCE="$ENDPOINT/store/temp/user/$USER/$FILE"
TPC_DEST="davs://redirector.t2.ucsd.edu:1094/store/temp/user/$USER/TPC/$RSE/$FILE"
transfer $TPC_SOURCE $TPC_DEST

# Test FTS TPC Endpoint as Destination
echo "Testing $ENDPOINT as destination"
TPC_SOURCE="davs://redirector.t2.ucsd.edu:1094/store/temp/user/$USER/TPC/$RSE/$FILE"
TPC_DEST="$ENDPOINT/store/temp/user/$USER/TPC_WRITE/$FILE"
transfer $TPC_SOURCE $TPC_DEST
