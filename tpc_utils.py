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

