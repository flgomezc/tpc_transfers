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


def download_file(url, new_filename,  macaroon, debug=0):
    if(debug == 1):
        command = ["curl", "-L", "--capath", "/etc/grid-security/certificates"]
    else:
        command = ["curl", "-s", "-L", "--capath", "/etc/grid-security/certificates"]
    command = command + ["-H", "'X-No-Delegate:true'"]
    command = command + ["--cacert", "/tmp/x509up_u52618", "-E", "/tmp/x509up_u52618", "-H", "'Credential: none'", "-m90"]
    command = command + ["-H", 'Authorization: Bearer '+macaroon]
    command = command + [url]
    if(new_filename is not None):
        command = command + ["-o", new_filename]
        
    log.debug(command) 
    out = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = out.communicate()
    if stderr is None:
        if(new_filename is None):
            log.debug("file content: "+stdout)
        else:
            log.debug("file was downladed: "+new_filename)
    else:
       log.error("Something went wrong when executing command:\n" +str(command))


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
    #-------------------------------------------------------------------------------

    macaroon = request_macaroon(url, "DOWNLOAD,DELETE,LIST", curl_debug)
    download_file(url, new_filename, macaroon, curl_debug)

log = logging.getLogger()    
if __name__ == "__main__":
    main()
