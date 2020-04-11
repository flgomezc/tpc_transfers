# This script is used to cook a curl command to get a checksum for a given url.
import sys
import logging
from tpc_utils import *

def main():
    #----- Config ----------------------------------------------------------------
    curl_debug = 1
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s  %(levelname)s - %(message)s', datefmt='%Y%m%d %H:%M:%S')
    
    url = sys.argv[1]
    new_filename = None
    if len(sys.argv) == 3:
        new_filename = sys.argv[2]
        log.info("Downloading: "+url+" as: "+new_filename)
    else:
        log.info("Showing content of: "+url)
    timeout = 120
    #-------------------------------------------------------------------------------
   
    tpc_util = TPC_util(log, timeout, curl_debug)
    macaroon = tpc_util.request_macaroon(url, "DOWNLOAD,DELETE,LIST")
    tpc_util.download_file(url, macaroon, new_filename)

log = logging.getLogger()    
if __name__ == "__main__":
    main()
