docker run -it  \
    --volume /Users/USERNAME/.globus/usercert.pem:/root/.globus/usercert.pem \
    --volume /Users/USERNAME/.globus/userkey.pem:/root/.globus/userkey.pem \
    --volume $(pwd)/tpc_transfers:/tpc_transfers \
    --env X509_USER_CERT=/root/.globus/usercert.pem \
    --env X509_USER_KEY=/root/.globus/userkey.pem \
    tx_client:latest
