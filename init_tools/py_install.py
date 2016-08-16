#!/usr/bin/python
#coding=utf8
#20141023. 20141030 add install sqlite-devel
import os
from sys import version
Error=[]
#Easy_list=['protobuf','web.py','redis','affinity','python-memcached','readline','zope.interface','flask','gevent','DBUtils','mysql-python','twisted']
Easy_list=['redis','gevent','mysql-python']
def Yum_install():
	comm="yum -y install gcc libxml2 libxml2-devel libxslt libxslt-devel gcc-c++ python-devel readline-devel mysql-devel openssl lynx openssl-devel sqlite-devel"
	Command(comm,'Yum_install')
	print '-'*20
def Python_update():
        ''' update python to 2.7.8'''
        py_version=version[:3]
        if float(py_version) < 2.7:
                comm='''cd /opt/ && wget https://www.python.org/ftp/python/2.7.8/Python-2.7.8.tgz && tar zxf Python-2.7.8.tgz && cd  Python-2.7.8 && \
                        ./configure --prefix=/usr/local/python &>/dev/null && make &>/dev/null && make install &>/dev/null && \
                        mv /usr/bin/python /usr/bin/python-%s && ln -s /usr/local/python/bin/python /usr/bin/python && \
                        sed -i '1s/python/python-%s/' /usr/bin/yum'''%(py_version,py_version)
		Command(comm,'Python_update')
        else:print "python is already 2.7 version" 
	print '-'*20
def Eazyinstall():
	''' install eazy_install'''	
	ifile="/usr/local/python/lib/python2.7/site-packages/setuptools.pth"
	comm='''cd /opt/ && wget https://pypi.python.org/packages/source/s/setuptools/setuptools-7.0.tar.gz  --no-check-certificate && \
		tar zxf setuptools-7.0.tar.gz && cd setuptools-7.0 && python setup.py install --prefix=/usr/local/python/ && \
		ln -s /usr/local/python//bin/easy_install  /usr/bin/easy_install'''
	if not os.path.exists(ifile):
		Command(comm,'Eazyinstall')
	else:print "easy_install is already install"
	print '-'*20
def Module_install():
	'''install The external module'''
	for i in Easy_list:
		comm="easy_install %s &>/dev/null"%i
		if i=='mysql-python':i='MySQLdb'
		if i=='python-memcached':i='memcache'
		if i=='protobuf':i='google.protobuf'
		if i=='web.py':i='web'
		try:
			exec('import %s'%i)
		except:
			if i=='twisted':
				os.curdir;os.chdir('Twisted-14.0.0')
				Command('python setup.py install &>/dev/null',i+' module')
			else:
				Command(comm,i+' module')
		else:
			print '%s module is already install'%i
	print '-'*20
#---------------------------------------------------------------------------------
def Command(comm,name):
	''' 命令执行 '''
	if os.system(comm)==0:
		print "\33[42m%s\33[0m\t\33[32m[OK]\33[0m"%name
        else:
                print "\33[1;35m%s\33[0m\t\33[31m[ERR]\33[0m"%name
		Error.append(name)
def Err():
        '''check err'''
        for i in Error:print "\33[1;35m%s\n%s\33[0m\t\33[31m[Failure]\33[0m"%('-'*20,i)
        if len(Error)>0:print "\33[5;31mError Num:\33[0m\t\33[31m%s\33[0m"%len(Error)
#########################################################################
if __name__ == "__main__":
	print "start Initialization..."
	Yum_install()
	#Python_update()
	Eazyinstall()
	Module_install()
	print "Initialization END."
	Err()
