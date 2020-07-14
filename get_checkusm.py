# This script is used to cook a curl command to get a checksum for a given url.
import sys
import logging
from tpc_utils import *

def main():
    #----- Config ----------------------------------------------------------------
    curl_debug = 1
    logging.basicConfig(level=logging.INFO, format='%(asctime)s  %(levelname)s - %(message)s', datefmt='%Y%m%d %H:%M:%S')
    
    url = sys.argv[1]
    log.info("Getting checksum for: "+url)
    timeout=10
    proxy= "/tmp/x509up_u0"
    #-------------------------------------------------------------------------------

    tpc_util = TPC_util(log, timeout, curl_debug, proxy)
    #macaroon = tpc_util.request_macaroon(url, "UPLOAD,DELETE,LIST")
    #macaroon = tpc_util.request_macaroon(url, "READ_METADATA,UPLOAD,DOWNLOAD,DELETE,MANAGE,UPDATE_METADATA,LIST")
    macaroon = tpc_util.request_macaroon(url, "READ_METADATA,DOWNLOAD,LIST")
    if macaroon:
        log.debug(macaroon)
    	adler32 = tpc_util.get_adler32(url, macaroon)
        if adler32:
           log.info(adler32)
        else:
           log.error("no checksum returned")

log = logging.getLogger()    
if __name__ == "__main__":
    main()
