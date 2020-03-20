# This script is used to cook a curl command to get a checksum for a given url.
import sys
import logging
import subprocess


def extract_macaroon(response):
    log.debug("response: "+response)
    macaroon = response.split('"')[3]
    return macaroon


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

def get_adler32(url, macaroon, debug=0):
    adler32 = -1
    if(debug == 1):
        command = ["curl", "-L", "--capath", "/etc/grid-security/certificates"]
    else:
        command = ["curl", "-s", "-L", "--capath", "/etc/grid-security/certificates"]
    command = command + ["-H", "'X-No-Delegate:true'"]
    command = command + ["-I", "-H", 'Want-Digest: adler32']
    command = command + ["--cacert", "/tmp/x509up_u52618", "-E", "/tmp/x509up_u52618", "-H", "'Credential: none'", "-m30"]
    command = command + ["-H", 'Authorization: Bearer '+macaroon]
    command = command + [url]
    out = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = out.communicate()
    if stderr is None:
        log.debug("file content: "+stdout)
        adler32 = extract_adler32(stdout)
    else:
       log.error("Something went wrong when executing command:\n" +str(command))

    return adler32

def extract_adler32(response):
    adler32 = None
    log.debug("response: "+response)
    for line in response.split("\n"):
        if "Digest" in line:
            adler32 = line.split("=")[1]
    return adler32 

def main():
    #----- Config ----------------------------------------------------------------
    curl_debug = 0
    logging.basicConfig(level=logging.INFO, format='%(asctime)s  %(levelname)s - %(message)s', datefmt='%Y%m%d %H:%M:%S')
    
    url = sys.argv[1]
    log.info("Getting checksum for: "+url)
    #-------------------------------------------------------------------------------

    macaroon = request_macaroon(url, "UPLOAD,DELETE,LIST", curl_debug)
    adler32 = get_adler32(url, macaroon, curl_debug)
    log.info("adler32: "+adler32)

log = logging.getLogger()    
if __name__ == "__main__":
    main()
