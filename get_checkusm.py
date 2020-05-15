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
    #-------------------------------------------------------------------------------

    tpc_util = TPC_util(log, timeout, curl_debug)
    #macaroon = tpc_util.request_macaroon(url, "UPLOAD,DELETE,LIST")
    macaroon = tpc_util.request_macaroon(url, "READ_METADATA,UPLOAD,DOWNLOAD,DELETE,MANAGE,UPDATE_METADATA,LIST")
    adler32 = tpc_util.get_adler32(url, macaroon)
    print(adler32)
    print(type(adler32))
    log.info("adler32: "+adler32)

log = logging.getLogger()    
if __name__ == "__main__":
    main()
