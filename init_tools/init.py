#!/usr/bin/python
#coding=utf-8
#create 2014.3.13 for centos6.4 autosetup
#2014.10.21 add : proc , Error check
#2014.10.22 add : python2.6 update to 2.7.8
#2014.10.23 add : Install zabbix_agent , add Command()
#2014.10.28 add : UsePAM no
#2014.10.29 change : proc={}
#2014.10.30 python update add : sqlite-devel

import os,re
from sys import version
Ip=os.popen("ifconfig eth0 | awk -F'[ :]+' '/inet /{print$4}' ").read()[:-1]
Zabbix_ServerIp='192.168.136.130'
comm={'1.ctrl-c':'grep "stty -echoctl" /etc/profile ||  echo "stty -echoctl" >> /etc/profile',
      '2.mail-check':'grep "unset MAILCHECK" /etc/profile || echo "unset MAILCHECK" >> /etc/profile',
      '3.ssh-speed':"sed -i 's/GSSAPIAuthentication yes/GSSAPIAuthentication no/' /etc/ssh/ssh_config",
      #'4.DNS-server':'echo "nameserver 8.8.8.8" > /etc/resolv.conf  && ping -c2 www.baidu.com',
      '5.time-ntp':"grep ntpdate /var/spool/cron/root || echo '0 */1 * * * /usr/sbin/ntpdate time.nist.gov;/sbin/clock -w' >> /var/spool/cron/root",
      '6.selinux-off':"sed -i 's/SELINUX=enforcing/SELINUX=disabled/' /etc/selinux/config && (setenforce 0 || getenforce)",
      #'7.yum-163':"cd /etc/yum.repos.d/ && wget http://mirrors.163.com/.help/CentOS6-Base-163.repo && yum clean all && echo yum makecache",
      '8.language-utf8':'LANG=zh_CN.UTF-8 && grep "LANG=zh_CN.UTF-8" /root/.bashrc || echo "export LANG=zh_CN.UTF-8" >> /root/.bashrc && locale',
      '9.ulimit':"egrep 'soft nofile|hard nofile' /etc/security/limits.conf || echo -e '* soft nofile 65536\n* hard nofile 65536' >>/etc/security/limits.conf && ulimit -HSn 65535",
      '10.user-root':"grep 'lifei ALL=(ALL) NOPASSWD:ALL' /etc/sudoers || echo 'lifei ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers",
      '11.ssh-UseDNS':"sed -i 's/#UseDNS yes/UseDNS no/' /etc/ssh/sshd_config",
      '12.ssh-UsePAM':"sed -i 's/^UsePAM.*/UsePAM no/' /etc/ssh/sshd_config",
     # '13.ssh-remote':"sed -i 's/^Defaults    requiretty/#Defaults    requiretty/' /etc/sudoers",
      '14.ssh-restart':"/etc/init.d/sshd restart",
      '15.ifstat-install':"cd /opt/ && wget http://distfiles.macports.org/ifstat/ifstat-1.1.tar.gz && tar zxf ifstat-1.1.tar.gz && cd ifstat-1.1 && ./configure >/dev/null && make && make install",
      #'16.yum-install':"yum -y install sqlite-devel"
      #'15.iftop-install':"yum -y install flex byacc libpcap ncurses ncurses-devel libpcap-devel &>/dev/null;cd /opt;wget http://www.ex-parrot.com/~pdw/iftop/download/iftop-0.17.tar.gz;tar zxf iftop-0.17.tar.gz;cd iftop-0.17;./configure;make;make install",
}
server=['ip6tables','postfix','bluetooth','cups']

proc={'TIME_WAIT最大数量	: tcp_max_tw_buckets=10000':'echo 10000 > /proc/sys/net/ipv4/tcp_max_tw_buckets',
'开启SYN Cookies防范少量SYN攻击 : net.ipv4.tcp_syncookies = 1':'echo 1 > /proc/sys/net/ipv4/tcp_syncookies',
'关闭 tcp_timestamps时间戳	: net.ipv4.tcp_timestamps = 0':'echo 0 > /proc/sys/net/ipv4/tcp_timestamps',
'TIME-WAIT重新用于新的TCP连接	: tcp_tw_reuse=1':'echo 1 >  /proc/sys/net/ipv4/tcp_tw_reuse', 
'二次握手尝试发送初始SYN,ACK数	: tcp_synack_retries=1':'echo 1 >  /proc/sys/net/ipv4/tcp_synack_retries', 
'新建连线尝试发送初始SYN次数	: tcp_syn_retries=1':'echo 1 >  /proc/sys/net/ipv4/tcp_syn_retries', 
'保持在FIN-WAIT-2状态的秒数	: tcp_fin_timeout=15':'echo 15 >  /proc/sys/net/ipv4/tcp_fin_timeout', 
'TCP发送keepalive消息的频度	: tcp_keepalive_time=1200':'echo 1200 >  /proc/sys/net/ipv4/tcp_keepalive_time', 
'探测没有确认时重新探测的频度	: tcp_keepalive_intvl=30':'echo 30 >  /proc/sys/net/ipv4/tcp_keepalive_intvl', 
'进行多少次探测			: tcp_keepalive_probes=5':'echo 5 >  /proc/sys/net/ipv4/tcp_keepalive_probes', 
}

Error=[]
##########################################################
def csh():
	'''环境初始化'''
	all=sorted(comm.items(),key=lambda x:int(re.findall('\d+',x[0])[0]))
	for project,action in all:
		Command(action,project)	
	print '='*20
########################################################################
def chk():
	'''关闭不用的服务'''
	for s in server:
		print os.popen('chkconfig %s off; chkconfig --list %s'%(s,s)).read(),
	print '='*20
#######################################################################
def pro():
	'''内核优化'''
	for project,action in proc.items():
		Command(action,project,colo='35')
		print '-'*20
	if os.system('modprobe bridge;sysctl -p &>/dev/null')==0:print "\33[1;35msysctl -p\33[0m\t\33[32m[OK]\33[0m"
#######################################################################
def audit():
	'''部署审计'''
	pfile='''
export HISTORY_FILE=/etc/share/`date +%Y-%m-%d`um.log
chown nobody:nobody $HISTORY_FILE &>/dev/null
chmod 002 $HISTORY_FILE &>/dev/null
chattr +a $HISTORY_FILE &>/dev/null
export PROMPT_COMMAND='{ date "+%y-%m-%d %T ##### $(who am i |awk "{print \$1\\" \\"\$2\\" \\"\$5}") #### $(pwd) #### $(id|awk "{print \$1}") #### $(history 1 | { read x cmd; echo "$cmd"; })"; } >>$HISTORY_FILE'
'''
	comm='''source /etc/profile ; if ! grep "chmod 002 /etc/share" /var/spool/cron/root &>/dev/null;then \
		echo "0 0 * * * /bin/touch /etc/share/\`date +\%Y-\%m-\%d\`um.log ; chmod 002 /etc/share/\`date +\%Y-\%m-\%d\`um.log" > /var/spool/cron/root;fi'''
	if os.system(''' sed -i "/HISTORY_FILE/d;/PROMPT_COMMAND/d" /etc/profile ''')==0:
		if not os.path.exists('/etc/share'):os.mkdir('/etc/share')
		with open("/etc/profile",'a') as f:f.write(pfile)
		os.popen(comm).read();print "\33[42maudit.sh\33[0m\t\33[32m[OK]\33[0m"
	print '='*20
#######################################################################
def timezone():
	'''修改时区'''
	print os.popen("/bin/cp -ar /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && sed -i 's#ZONE=.*#ZONE=Asia/Shanghai#g'  /etc/sysconfig/clock && /usr/sbin/ntpdate time.nist.gov ;/sbin/clock -w").read(),
	print '='*20
#########################################################################
def hostname():
	'''修改主机名'''
        yn=raw_input("are you set hostname?(y/n)")
	if yn=='y':
		host=raw_input("please input IDC number for hostname:")
		hostfile=open('/etc/sysconfig/network').read()
		with open('/etc/sysconfig/network','w') as f:
			f.write(re.sub('HOSTNAME=.*','HOSTNAME=%s'%host,hostfile))
		print open('/etc/sysconfig/network').read()
	print '='*20
#########################################################################
def Zabbix_agent():
	'''install Zabbix_agent'''
	comm='''rpm -ivh http://repo.zabbix.com/zabbix/2.4/rhel/6/x86_64/zabbix-release-2.4-1.el6.noarch.rpm ; \
		yum -y install zabbix-agent ; sed -i 's/^Server=.*/Server=%s/' /etc/zabbix/zabbix_agentd.conf && \
		/etc/init.d/zabbix-agent restart'''%Zabbix_ServerIp
	if os.system("[ -f /etc/init.d/zabbix-agent ]")!=0:
		Command(comm,'Zabbix_agent_install')
	else:print("Zabbix_agent is already install")
#########################################################################
def python_startup():
	'''python tab'''
	pystart='''import readline, rlcompleter; readline.parse_and_bind("tab: complete")'''
	os.popen('''echo '%s' > /root/.pythonstartup.py'''%pystart).read()
	if os.system("grep pythonstart /root/.bashrc &>/dev/null")!=0:
		os.popen('''echo "export PYTHONSTARTUP=~/.pythonstartup.py" >> /root/.bashrc''').read()
	print "\33[42mpytonstartup\33[0m\t\33[32m[OK]\33[0m"
	print '='*20
#########################################################################
def python_update():
	''' update python to 2.7.8'''
	py_version=version[:3]
	if float(py_version) < 2.7:
		comm='''yum -y install sqlite-devel readline-devel* zlib zlib-devel openssl-devel && \
            cd /opt/ && wget https://www.python.org/ftp/python/2.7.8/Python-2.7.8.tgz && tar zxf Python-2.7.8.tgz && \
			cd  Python-2.7.8 && ./configure --prefix=/usr/local/python &>/dev/null && make &>/dev/null && make install &>/dev/null && \
			mv /usr/bin/python /usr/bin/python-%s && ln -s /usr/local/python/bin/python /usr/bin/python && \
			sed -i '1s/python/python-%s/' /usr/bin/yum'''%(py_version,py_version)
		Command(comm,'python_update')
	else:print "python is already 2.7 version" 
	print '='*20
#########################################################################
def Command(comm,name,colo='42'):
        ''' 命令执行 '''
        if os.system(comm)==0:
                print "\33[1;%sm%s\33[0m\t\33[32m[OK]\33[0m"%(colo,name)
        else:
                print "\33[1;35m%s\33[0m\t\33[31m[ERR]\33[0m"%name
                Error.append(name)
def Err():
	'''check err'''
	for i in Error:
		print "\33[1;35m%s\n%s\33[0m\t\33[31m[Failure]\33[0m"%('-'*20,i)
	if len(Error)>0:print "\33[5;31mError Num:\33[0m\t\33[31m%s\33[0m"%len(Error)
#########################################################################
if __name__ == "__main__":
	print "start Initialization..."
	csh()
	chk()
	pro()
	audit()
	#timezone()
	#hostname()
	#Zabbix_agent()
	python_startup()
	python_update()
	print "Initialization END."
	Err()
