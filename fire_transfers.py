import sys
import argparse
import logging
import time
import subprocess
import pdb
#pdb.set_trace()

def extract_macaroon(response):
    log.debug("response: "+response)
    macaroon = response.split('"')[3]
    return macaroon

#def macaroon_download(token, source, dest):
#curl --verbose --connect-timeout 60 -D /tmp/tmp.i9Au4JQ9Rd -s -f -L --capath /etc/grid-security/certificates -H 'X-No-Delegate:true' --cacert p/x509up_u52618 -E /tmp/x509up_u52618 -H 'Credential: none' -m30 -T /bin/bash  -H 'Authorization: Bearer MDAxOGxvY2F0aW9uIFQyX1VTX1VDU0QKMDAzNGlkZW50aWZpZXIgMjlhN2JhZGUtZTYzMC00MTFhLWI3NjEtZjllODU5MjhmOTY0CjAwMTVjaWQgbmFtZTpkZGF2aWxhCjAwNTJjaWQgYWN0aXZpdHk6UkVBRF9NRVRBREFUQSxVUExPQUQsRE9XTkxPQUQsREVMRVRFLE1BTkFHRSxVUERBVEVfTUVUQURBVEEsTElTVAowMDJkY2lkIGFjdGl2aXR5OkRPV05MT0FELFVQTE9BRCxERUxFVEUsTElTVAowMDJiY2lkIHBhdGg6L3N0b3JlL3VzZXIvZGRhdmlsYS9oZWxsby0wMDEKMDAyNGNpZCBiZWZvcmU6MjAyMC0wMS0zMVQxNzoxMzowMVoKMDAyZnNpZ25hdHVyZSBuit4Um8XXFbKdCK2LBAZOwiqFj3JPG-XF3dLFAFriJgo' https://redirector.t2.ucsd.edu:1094//store/user/ddavila/hello-001

def download_file(url, macaroon, debug=0):
    if(debug == 1):
        command = ["curl", "-L", "--capath", "/etc/grid-security/certificates"]
    else:
        command = ["curl", "-s", "-L", "--capath", "/etc/grid-security/certificates"]
    command = command + ["-H", "'X-No-Delegate:true'"]
    command = command + ["--cacert", "/tmp/x509up_u52618", "-E", "/tmp/x509up_u52618", "-H", "'Credential: none'", "-m30"]
    command = command + ["-H", 'Authorization: Bearer '+macaroon]
    command = command + [url]
    out = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = out.communicate()
    if stderr is None:
        log.debug("file content: "+stdout)
    else:
       log.error("Something went wrong when executing command:\n" +str(command))

def tpc(url_src, macaroon_src, url_dst, macaroon_dst, debug=0):
    res = -1
    if(debug == 1):
        command = ["curl", "-L", "--capath", "/etc/grid-security/certificates"]
    else:
        command = ["curl", "-s", "-L", "--capath", "/etc/grid-security/certificates"]
    command = command + ["-H", "'X-No-Delegate:true'"]
    command = command + ["--cacert", "/tmp/x509up_u52618", "-E", "/tmp/x509up_u52618", "-H", "'Credential: none'", "-m30"]
    command = command + ["-X", "COPY"]
    command = command + ["-H", 'TransferHeaderAuthorization: Bearer '+macaroon_src]
    command = command + ["-H", 'Source: '+url_src]
    command = command + ["-H", 'Authorization: Bearer '+macaroon_dst]
    command = command + [url_dst]
    out = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = out.communicate()
    if stderr is None:
        log.debug("TPC OK")
        res = 0
    else:
        log.error("Something went wrong when executing command:\n" +str(command))
        res = 1

    return res

def request_macaroon(url, permission_list, debug=0):
    macaroon = None
    if(debug == 1):
        command = ["curl", "-L", "--capath", "/etc/grid-security/certificates"]
    else:
        command = ["curl", "-s", "-L", "--capath", "/etc/grid-security/certificates"]
    command = command + ["-H", "'X-No-Delegate:true'"]
    command = command + ["--cacert", "/tmp/x509up_u52618", "-E", "/tmp/x509up_u52618", "-H", "'Credential: none'", "-m30"]
    command = command + ["-X", "POST"]
    command = command + ["-H", 'Content-Type: application/macaroon-request']
    command = command + ["-d"]
    command = command + ['{"caveats": ["activity:'+permission_list+'"], "validity": "PT30M"}']
    command = command + [url]
    
    out = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = out.communicate()
    if stderr is None:
        macaroon = extract_macaroon(stdout)
        log.debug("macaroon: "+macaroon)
    else:
        log.error("Something went wrong when executing command:\n" +str(command))

    return macaroon


def main():
    #----- Config ----------------------------------------------------------------
    curl_debug = 0
    logging.basicConfig(level=logging.INFO, format='%(asctime)s  %(levelname)s - %(message)s', datefmt='%Y%m%d %H:%M:%S')
    # Total number of transfers
    total_transfers = 2
    # Time between transfers
    time_between_tx = 30
    # Suffix for destination file. Destination file is same as source file + suffix
    suffix = "_20200319"
    
    #url_base_src = "https://xrootd.rcac.purdue.edu:1094/store/temp/user/ddavila/"
    #url_base_dst = "https://redirector.t2.ucsd.edu:1094//store/user/ddavila/LoadTest_purdue/"
    url_base_src = "https://xrootd.rcac.purdue.edu:1094/store/PhEDEx_LoadTest07/LoadTest07_Debug_Purdue/"
    url_base_dst = "https://redirector.t2.ucsd.edu:1094//store/user/ddavila/LoadTest_purdue/"
    
    load_tests_filename = sys.argv[1]
    log.debug("Reading list of files from: "+load_tests_filename)
    fd = open(load_tests_filename)

    # List of the endpoint + LoadTest files samples, e.g.
    # davs://xrootd.rcac.purdue.edu:1094/store/PhEDEx_LoadTest07/LoadTest07_Debug_Purdue/LoadTest07_Purdue_3E
    load_test_list =  fd.readlines()

    i=0
    while(i < total_transfers):
        file_src = load_test_list[i][:-1]
        file_dst = file_src + suffix
        url_src = url_base_src + file_src
        url_dst = url_base_dst + file_dst
        log.info("File to transfer: "+url_src)
        log.debug("TPC: "+url_src+" -> "+url_dst)
       
        # Get macaroons
        log.info(file_src +" Requesting macaroons")
        macaroon_src = request_macaroon(url_src, "DOWNLOAD,DELETE,LIST", curl_debug)
        macaroon_dst = request_macaroon(url_dst, "UPLOAD,DELETE,LIST", curl_debug)
        
        # Start TPC
        log.info(file_src +" starting transfer")
        res = tpc(url_src, macaroon_src, url_dst, macaroon_dst, curl_debug)
        log.info(file_src +" transfer done, res: "+str(res))
        i = i+1
        if i < total_transfers: 
            time.sleep(time_between_tx)

log = logging.getLogger()    
if __name__ == "__main__":
    main()
