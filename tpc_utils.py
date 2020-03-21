import subprocess

class TPC_util:
    def __init__(self, log, debug):
        self.log = log
        self.debug = debug
    
    def extract_macaroon(self, response):
        self.log.debug("response: "+response)
        macaroon = response.split('"')[3]
        return macaroon
    
    
    def request_macaroon(self, url, permission_list):
        macaroon = None
        if(self.debug == 1):
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
            macaroon = self.extract_macaroon(stdout)
            self.log.debug("macaroon: "+macaroon)
        else:
            self.log.error("Something went wrong when executing command:\n" +str(command))
    
        return macaroon
    
    
    def download_file(self, url,  macaroon, new_filename=None):
        if(self.debug == 1):
            command = ["curl", "-L", "--capath", "/etc/grid-security/certificates"]
        else:
            command = ["curl", "-s", "-L", "--capath", "/etc/grid-security/certificates"]
        command = command + ["-H", "'X-No-Delegate:true'"]
        command = command + ["--cacert", "/tmp/x509up_u52618", "-E", "/tmp/x509up_u52618", "-H", "'Credential: none'", "-m90"]
        command = command + ["-H", 'Authorization: Bearer '+macaroon]
        command = command + [url]
        if(new_filename is not None):
            command = command + ["-o", new_filename]
            
        self.log.debug(command) 
        out = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout, stderr = out.communicate()
        if stderr is None:
            if(new_filename is None):
                self.log.debug("file content: "+stdout)
            else:
                self.log.debug("file was downladed: "+new_filename)
        else:
           self.log.error("Something went wrong when executing command:\n" +str(command))
    
    def get_adler32(self, url, macaroon):
        adler32 = -1
        if(self.debug == 1):
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
            self.log.debug("file content: "+stdout)
            adler32 = self.extract_adler32(stdout)
        else:
           self.log.error("Something went wrong when executing command:\n" +str(command))
    
        return adler32
    
    def extract_adler32(self, response):
        adler32 = None
        self.log.debug("response: "+response)
        for line in response.split("\n"):
            if "Digest" in line:
                adler32 = line.split("=")[1]
        return adler32 
    
    
    def tpc(self, url_src, macaroon_src, url_dst, macaroon_dst):
        res = -1
        if(self.debug == 1):
            command = ["curl", "-L", "--capath", "/etc/grid-security/certificates"]
        else:
            command = ["curl", "-s", "-L", "--capath", "/etc/grid-security/certificates"]
        command = command + ["-H", "'X-No-Delegate:true'"]
        command = command + ["--cacert", "/tmp/x509up_u52618", "-E", "/tmp/x509up_u52618", "-H", "'Credential: none'", "-m120"]
        command = command + ["-X", "COPY"]
        command = command + ["-H", 'TransferHeaderAuthorization: Bearer '+macaroon_src]
        command = command + ["-H", 'Source: '+url_src]
        command = command + ["-H", 'Authorization: Bearer '+macaroon_dst]
        command = command + [url_dst]
        out = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout, stderr = out.communicate()
        if stderr is None:
            self.log.debug("TPC OK")
            res = 0
        else:
            self.log.error("Something went wrong when executing command:\n" +str(command))
            res = 1
    
        return res

