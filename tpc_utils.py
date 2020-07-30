import subprocess
import pdb

class TPC_util:
    def __init__(self, log, timeout, debug, proxy):
        self.log = log
        self.proxy = proxy
        self.timeout = "-m"+str(timeout)
        self.debug = debug
   
    def get_command_str(self, command):
        command_str = ""
        for i in command:
            command_str+=i+" "
        return command_str[:-1]
 
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
        command = command + [self.timeout]
        command = command + ["-H", "'X-No-Delegate:true'"]
        command = command + ["--cacert", self.proxy, "-E", self.proxy, "-H", "'Credential: none'"]
        command = command + ["-X", "POST"]
        command = command + ["-H", 'Content-Type: application/macaroon-request']
        command = command + ["-d"]
        command = command + ['{"caveats": ["activity:'+permission_list+'"], "validity": "PT30M"}']
        command = command + [url]
        
        out = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout, stderr = out.communicate()
        if out.returncode ==0:
            macaroon = self.extract_macaroon(stdout)
            self.log.debug("macaroon: "+macaroon)
            print(self.get_command_str(command))

        else:
            self.log.error("Something went wrong when executing command:\n" +self.get_command_str(command))
    
        return macaroon
    
    def get_byte_range(self, url,  macaroon, start, end):
        if(self.debug == 1):
            command = ["curl", "-L", "--capath", "/etc/grid-security/certificates"]
        else:
            command = ["curl", "-s", "-L", "--capath", "/etc/grid-security/certificates"]
        command = command + [self.timeout]
        command = command + ["-H", "'X-No-Delegate:true'"]
        command = command + ["-H", "'Range: bytes="+start+"-"+end+"'"]
        command = command + ["--cacert", self.proxy, "-E", self.proxy, "-H", "'Credential: none'"]
        command = command + ["-H", 'Authorization: Bearer '+macaroon]
        command = command + [url]
        self.log.debug(str(command)) 
        out = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout, stderr = out.communicate()
        if out.returncode ==0:
            self.log.debug("stdout:\n"+stdout)
            self.log.debug("file content: "+stdout)
        else:
           self.log.error("Something went wrong when executing command:\n" +str(command))
           self.log.debug("stdout:\n "+stdout)
 
    def download_file(self, url,  macaroon, new_filename=None):
        if(self.debug == 1):
            command = ["curl", "-L", "--capath", "/etc/grid-security/certificates"]
        else:
            command = ["curl", "-s", "-L", "--capath", "/etc/grid-security/certificates", "-H", "'Credential: none'"]
        command = command + [self.timeout]
        command = command + ["-H", "'X-No-Delegate:true'"]
        if not macaroon:
        	command = command + ["--cacert", self.proxy, "-E", self.proxy]
	else:
        	command = command + ["-H", 'Authorization: Bearer '+macaroon]
        command = command + [url]
        if(new_filename is not None):
            command = command + ["-o", new_filename]
        #pdb.set_trace()    
        self.log.debug(str(command)) 
        out = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout, stderr = out.communicate()
        if out.returncode == 0:
            self.log.debug("stdout:\n"+stdout)
            if(new_filename is None):
                self.log.debug("file content: "+stdout)
            else:
                self.log.debug("file was downladed: "+new_filename)
        else:
           self.log.error("Something went wrong when executing command:\n" +str(command))
           self.log.debug("stdout:\n "+stdout)
    
    def get_adler32(self, url, macaroon):
        adler32 = -1
        if(self.debug == 1):
            command = ["curl", "-L", "--capath", "/etc/grid-security/certificates"]
        else:
            command = ["curl", "-s", "-L", "--capath", "/etc/grid-security/certificates"]
        command = command + [self.timeout]
        command = command + ["-H", "'X-No-Delegate:true'"]
        command = command + ["-I", "-H", 'Want-Digest: adler32', "-H", "'Credential: none'"]
        if not macaroon:
            command = command + ["--cacert", self.proxy, "-E", self.proxy]
        else:
            command = command + ["-H", 'Authorization: Bearer '+macaroon]
        command = command + [url]
        self.log.debug(self.get_command_str(command))
        out = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout, stderr = out.communicate()
        if out.returncode == 0:
            self.log.debug("file content: "+stdout)
            adler32 = self.extract_adler32(stdout)
        else:
           self.log.error("Something went wrong when executing command:\n" +self.get_command_str(command))
    
        return adler32
    
    def extract_adler32(self, response):
        adler32 = None
        self.log.debug("response: "+response)
        for line in response.split("\n"):
            if "Digest" in line:
                adler32 = line.split("=")[1]
        return adler32 
    
    def execute_cmd(self, cmd):
        popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
        for stdout_line in iter(popen.stdout.readline, ""):
            yield stdout_line 
        popen.stdout.close()
        return_code = popen.wait()
        if return_code:
            raise subprocess.CalledProcessError(return_code, cmd)

    
    def tpc(self, url_src, macaroon_src, url_dst, macaroon_dst):
        res = -1
        if(self.debug == 1):
            command = ["curl","-v", "-L", "--capath", "/etc/grid-security/certificates"]
        else:
            command = ["curl", "-s", "-L", "--capath", "/etc/grid-security/certificates"]
        command = command + [self.timeout]
        command = command + ["-H", "'X-No-Delegate:true'"]
        command = command + ["-X", "COPY"]
        command = command + ["-H", 'TransferHeaderAuthorization: Bearer '+macaroon_src]
        command = command + ["-H", 'Source: '+url_src]
        command = command + ["-H", 'Authorization: Bearer '+macaroon_dst]
        command = command + [url_dst]
	for line in self.execute_cmd(command):
            print(line)	

    def tpc_bak(self, url_src, macaroon_src, url_dst, macaroon_dst):
        res = -1
        if(self.debug == 1):
            command = ["curl","-v", "-L", "--capath", "/etc/grid-security/certificates"]
        else:
            command = ["curl", "-s", "-L", "--capath", "/etc/grid-security/certificates"]
        command = command + [self.timeout]
        command = command + ["-H", "'X-No-Delegate:true'"]
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

