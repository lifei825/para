#!/usr/bin/python
# -*- coding: utf-8 -*-
#2014.926 add moudule getopt
#20150513 py3版本 同时支持密钥(NOPASSWD标记密码)及密码认证
#iplist:"192.168.1.xxx prot username NOPASSWD"
import paramiko,multiprocessing,os,re
from sys import argv,getdefaultencoding
from getopt import getopt,GetoptError
import time
#reload(__import__('sys')).setdefaultencoding('utf-8')
#print getdefaultencoding()


def ssh2(ip,port,user,passwd,cmd):
        try:
            #paramiko.util.log_to_file('paramiko.log')
            pkey='/home/hamlet/.ssh/id_rsa'
            key=paramiko.RSAKey.from_private_key_file(pkey)
            ssh=paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.load_system_host_keys()
            if passwd == 'NOPASSWD':
                ssh.connect(ip,port=port,username=user,pkey=key,timeout=10)
            else:
                ssh.connect(ip,port=port,username=user,password=passwd,timeout=10)
            stdin, stdoutt, stderr = ssh.exec_command(cmd)
            out = stdoutt.readlines()
            for i in out:
               print('[%s]\t%s'%(ip,i),end='')
               Log('[%s]\t%s'%(ip,i))
            ssh.close()
        except:
            print('[%s]\tCmd Error\n'%ip)   
            Log('[%s]\tCmd Error\n'%ip)

def upload(ip,port,user,passwd,local_file,remote_file):
       up=paramiko.Transport((ip,port))
       up.connect(username=user,password=passwd)
       sftp=paramiko.SFTPClient.from_transport(up)
       try:
           sftp.put(local_file,remote_file)
       except:
           print('[%s]\tupload some Error\n'%ip)
           Log('[%s]\tupload some Error\n'%ip)
       else:
           print('[%s]\tupload %s to %s OK\n'%(ip,local_file,ip))
           Log('[%s]\tupload %s to %s OK\n'%(ip,local_file,ip))
       up.close()

def download(ip,port,user,passwd,local_file,remote_file):
       down=paramiko.Transport((ip,port))
       down.connect(username=user,password=passwd)
       sftp=paramiko.SFTPClient.from_transport(down)
       try:
           sftp.get(remote_file,local_file)
       except:
           print('[%s]\tdownload some Error\n'%ip)
       else:
           print('[%s]\tdownload %s from %s OK\n'%(ip,remote_file,ip))
       down.close()

def Log(l):
        log=open('para.log','a')
        log.write(l)
        log.close()
        
def main(ip_file,con_file):
        iplist=open(ip_file).readlines()
        num=len(iplist)
        for x in open(con_file).readlines():
                multi=[]
                if x.startswith('com:'):
                        cmd=re.findall('com:(.*)',x)
                        for i in range(num):        
                                ip,port,user,passwd=iplist[i].split();port=int(port)
                                p=multiprocessing.Process(target=ssh2,args=(ip,port,user,passwd,cmd[0],))
                                multi.append(p)
                        
                        for i in range(num):
                                multi[i].start()

                        for i in range(num):
                                multi[i].join()
                elif x.startswith('up'):
                        up,local_file,remote_file,nn=re.split(':| * |\n',x)
                        for i in range(num):        
                                ip,port,user,passwd=iplist[i].split();port=int(port)
                                p=multiprocessing.Process(target=upload,args=(ip,port,user,passwd,local_file,remote_file,))
                                multi.append(p)

                        for i in range(num):
                                multi[i].start()

                        for i in range(num):
                                multi[i].join()

                elif x.startswith('down'):
                        down,remote_file,local_file,nn=re.split(':| * |\n',x)
                        for i in range(num):        
                                ip,port,user,passwd=iplist[i].split();port=int(port)
                                p=multiprocessing.Process(target=download,args=(ip,port,user,passwd,local_file,remote_file,))
                                multi.append(p)

                        for i in range(num):
                                multi[i].start()

                        for i in range(num):
                                multi[i].join()
                         


if __name__=='__main__':
        direct_run=False
        if os.path.exists('para.log'):os.popen('rm -f para.log');os.popen('touch para.log')
        #set parameters
        try:
                options,args=getopt(argv[1:],"hyl:c:",["help","iplist=","config="])
        except GetoptError as wr:
                print("Error:",wr)
                print('Plese input: python %s -l iplist -c conf (-y)'%argv[0]);exit()
        #To confirm the meaning of parameters
        for opt,val in options:
                if opt in ('-h','--help'):
                        print('''
\t#############--HELP--###########################
\t#  -l iplist) 192.168.1.x port user passwd     #
\t#  -c config) com:命令；up：上传；down：下载   #  
\t################################################
''')
                        exit()
                elif opt=='-l':
                        if os.path.exists(val):
                                ip_file=val
                        else:
                                print(val,"not exists");exit()
                elif opt=='-c':
                        if os.path.exists(val):
                                con_file=val
                        else:
                                print(val,"not exists");exit()
                elif opt=='-y':
                        direct_run=True
        #running
        if direct_run and globals().get('ip_file') and globals().get('con_file'):
                first=time.time()
                main(ip_file,con_file)
                last=time.time()
        elif direct_run==False and globals().get('ip_file') and globals().get('con_file'):
                #new conf
                if os.path.exists('confend'):os.popen('rm -f confend')
                for i in open(con_file).readlines():
                        if not i.startswith('#') and not i.startswith('\n'):
                                conf2=open('confend','a');conf2.write(i);conf2.close()
                print("\033[1;31;40mcheck config:\n%s\033[0m"%open('confend').read())
                #ready
                yn=input("are you continue(y/n)")
                if yn=='y':
                        first=time.time()
                        main(ip_file,con_file)
                        last=time.time()
                else:
                        exit()
        else:
                print('Plese input: python %s -l iplist -c conf (-y)'%argv[0]);exit()
        
        #last check run_time , yes or no
        print('\033[36;40mUse time:%.5f\033[0m'%(last-first))   
        num=os.popen("awk '{print$1}' para.log | sort -n | uniq  | wc -l").read()[:-1]
        err_num=os.popen("grep Error para.log  | sort -n | uniq  | wc -l").read()[:-1]
        print("\033[1;32;40mAll Run Num:%s\033[0m"%num)
        print("\033[1;31;40mERR Num:%s\033[0m"%err_num)
        #err ip
        print('='*50)
        iplist=re.findall('(\d+.\d+.\d+.\d+)',open(ip_file).read())
        iplog=re.findall('\[(\d+.\d+.\d+.\d+)\]\t',open('para.log').read())
        for i in set(iplist)-set(iplog):print("\033[1;35;40mERR IP:%s\033[0m"%i)

                


#ssh2('192.168.1.111',22,'root','123','free -m;ls -lh')
