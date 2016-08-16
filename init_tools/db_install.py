#!/usr/bin/python
#coding=utf8
#20141023
import os
Error=[]
DBpasswd='root'
DBsql='dragon.sql'
def Yum_install():
	comm="rpm -Uvh http://mirror.webtatic.com/yum/el6/latest.rpm ; \
	      yum remove mysql-libs -y ; yum install tcl mysql55w-devel mysql55w-server --enablerepo=webtatic"
	Command(comm,'Yum_install')
	print '-'*20
def Mysql_init():
	'''MYSQL Initialization'''
	comm='''chkconfig --level 345 mysqld on && /etc/init.d/mysqld start && \
		mysqladmin -u root password '%s' && \
		mysql -uroot -p'%s' -e "DROP DATABASE test;DELETE FROM mysql.user WHERE user = '';" ; \
		echo -e '[mysql]\nprompt="\u@\h [\d]>"' >> /etc/my.cnf'''%(DBpasswd,DBpasswd)
	if os.system("mysql -uroot -p'%s' -e 'show processlist;' &>/dev/null")!=0:
		Command(comm,'MYSQL Initialization')
	else:
		print 'MYSQL is already Initialization'
	print '-'*20
def Create_sql():
	'''import dragon.sql'''
	comm='''mysql -uroot -p'%s' -e "create database dragon" && \
		mysql -uroot -p'%s' dragon < %s'''%(DBpasswd,DBpasswd,DBsql)
	if os.system("mysql -uroot -p'%s' -e 'show databases;'|grep dragon"%DBpasswd)!=0:
		Command(comm,'MYSQL import sql')
	else:
		print 'MYSQL is already Import sql'
	print '-'*20
def Redis_install():
	comm='''yum install tcl;cd /usr/local/ && wget http://download.redis.io/releases/redis-2.8.17.tar.gz && \
		tar xzf redis-2.8.17.tar.gz && cd redis-2.8.17 && make test &>/dev/null && \
		make install'''
	if os.system("[ -f /usr/local/bin/redis-server ]")!=0:
		Command(comm,'Redis_install')
        else:
                print 'Redis is already Install'
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
	#Yum_install()
	#Mysql_init()
	#Create_sql()
	Redis_install()
	print "Initialization END."
	Err()
