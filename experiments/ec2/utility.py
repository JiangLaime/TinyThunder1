import argparse
import boto.ec2
import gevent
from fabric import task, Connection, Config
from fabric import ThreadingGroup
from gevent import Greenlet

import sys, os
import time

from invoke import Responder

if not boto.config.has_section('ec2'):
    boto.config.add_section('ec2')
    boto.config.setbool('ec2','use-sigv4',True)

secgroups = {
    'us-east-2':'sg-0c5a853c448c66a98',
    # 'us-east-1':'sg-6c4dfe0a',
    # 'us-west-1':'sg-7b34651e',
    # 'us-west-2':'sg-8f067ceb',
    # 'eu-west-1':'sg-368c3152',
    # 'sa-east-1':'sg-2a1f744f',
    # 'ap-southeast-1':'sg-2d491c48',
    # 'ap-southeast-2':'sg-d58dd4b0',
    # 'ap-northeast-1':'sg-499fb02c',
#    'eu-central-1':'sg-2bfe9342'  # somehow this group does not work
}
regions = sorted(secgroups.keys())[::-1]

NameFilter = 'Badger'
    
def getAddrFromEC2Summary(s):
    return [
            x.split('ec2.')[-1] for x in s.replace(
                '.compute.amazonaws.com', ''
                ).replace(
                    '.us-west-1', ''    # Later we need to add more such lines
                    ).replace(
                        '-', '.'
                        ).strip().split('\n')]

def get_ec2_instances_ip(region):
    ec2_conn = boto.ec2.connect_to_region(region,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key)
    if ec2_conn:
        result = []
        # reservations = ec2_conn.get_all_reservations(filters={'tag:Name': NameFilter})
        reservations = ec2_conn.get_all_reservations()
        for reservation in reservations:
            if reservation:       
                for ins in reservation.instances:
                    if ins.public_dns_name: 
                        currentIP = ins.public_dns_name.split('.')[0][4:].replace('-','.')
                        result.append(currentIP)
                        print (currentIP)
        return result
    else:
        print ('Region failed', region)
        return None

def get_ec2_instances_id(region):
    ec2_conn = boto.ec2.connect_to_region(region,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key)
    if ec2_conn:
        result = []
        reservations = ec2_conn.get_all_reservations(filters={'tag:Name': NameFilter})
        for reservation in reservations:    
            for ins in reservation.instances:
                print (ins.id)
                result.append(ins.id)
        return result
    else:
        print ('Region failed', region)
        return None

def stop_all_instances(region):
    ec2_conn = boto.ec2.connect_to_region(region,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key)
    idList = []
    if ec2_conn:
        reservations = ec2_conn.get_all_reservations(filters={'tag:Name': NameFilter})
        for reservation in reservations: 
            if reservation:   
                for ins in reservation.instances:
                    idList.append(ins.id)
        ec2_conn.stop_instances(instance_ids=idList)

def terminate_all_instances(region):
    ec2_conn = boto.ec2.connect_to_region(region,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key)
    idList = []
    if ec2_conn:
        reservations = ec2_conn.get_all_reservations(filters={'tag:Name': NameFilter})
        for reservation in reservations:   
            if reservation:    
                for ins in reservation.instances:
                    idList.append(ins.id)
        ec2_conn.terminate_instances(instance_ids=idList)

def launch_new_instances(region, number):
    ec2_conn = boto.ec2.connect_to_region(region,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key)
    dev_sda1 = boto.ec2.blockdevicemapping.EBSBlockDeviceType(delete_on_termination=True)
    dev_sda1.size = 8 # size in Gigabytes
    dev_sda1.delete_on_termination = True
    bdm = boto.ec2.blockdevicemapping.BlockDeviceMapping()
    bdm['/dev/sda1'] = dev_sda1
    img = ec2_conn.get_all_images(filters={'name':'ubuntu/images/hvm-ssd/ubuntu-trusty-14.04-amd64-server-20150325'})[0].id
    reservation = ec2_conn.run_instances(image_id=img, #'ami-df6a8b9b',  # ami-9f91a5f5
                                 min_count=number,
                                 max_count=number,
                                 key_name='amiller-mc2ec2', 
                                 instance_type='t2.medium',
                                 security_group_ids = [secgroups[region], ],
                                 block_device_map = bdm)
    for instance in reservation.instances:
        instance.add_tag("Name", NameFilter)
    return reservation


def start_all_instances(region):
    ec2_conn = boto.ec2.connect_to_region(region,
                aws_access_key_id=access_key,
                 aws_secret_access_key=secret_key)
    idList = []
    if ec2_conn:
        reservations = ec2_conn.get_all_reservations(filters={'tag:Name': NameFilter})
        for reservation in reservations:    
            for ins in reservation.instances:
                idList.append(ins.id)
        ec2_conn.start_instances(instance_ids=idList)


def ipAll():
    result = []
    for region in regions:
        result += get_ec2_instances_ip(region) or []
    open('hosts','w').write('\n'.join(result))
    group = ThreadingGroup(','.join(result))
    group.run('rm ~/hosts',warn=True)
    group.put('./hosts', '/home/admin/hosts')
    return result

def syncKeys():
    hosts = ','.join([l for l in open('hosts', 'r').read().split('\n') if l])
    ThreadingGroup(hosts).put('./*.keys', '/home/admin/hosts')

def install_dependencies():
    hosts0 = [l for l in open('hosts', 'r').read().split('\n') if l]
    hosts1 = ','.join([l for l in open('hosts', 'r').read().split('\n') if l])
    group = ThreadingGroup(hosts1)
    sudopass = Responder(
        pattern=r'\[sudo\] password:',
        response='asdasd\n',
    )
    group.sudo('apt-get update',pty=True,watchers=[sudopass])
    group.sudo('apt-get -y install python3-gevent',pty=True,watchers=[sudopass])
    group.sudo('apt-get -y install git',pty=True,watchers=[sudopass])
    group.sudo('apt-get -y install python3-socks',pty=True,watchers=[sudopass])
    group.sudo('apt-get -y install python3-pip',pty=True,watchers=[sudopass])
    group.sudo('apt-get -y install python3-dev',pty=True,watchers=[sudopass])
    group.sudo('apt-get -y install python3-gmpy2',pty=True,watchers=[sudopass])
    group.sudo('apt-get -y install flex',pty=True,watchers=[sudopass])
    group.sudo('apt-get -y install bison',pty=True,watchers=[sudopass])
    group.sudo('apt-get -y install libgmp-dev',pty=True,watchers=[sudopass])
    group.sudo('apt-get -y install libssl-dev',pty=True,watchers=[sudopass])
    group.sudo('pip3 install pycrypto',pty=True,watchers=[sudopass])
    group.sudo('pip3 install ecdsa',pty=True,watchers=[sudopass])
    group.sudo('pip3 install zfec',pty=True,watchers=[sudopass])
    group.sudo('pip3 install gipc',pty=True,watchers=[sudopass])
    group.run('wget https://crypto.stanford.edu/pbc/files/pbc-0.5.14.tar.gz')
    group.run('tar -xvf pbc-0.5.14.tar.gz',hide=True)



    def installcharm(h):
        conn = Connection(h)
        conn.run('git clone https://github.com/JHUISI/charm.git')
        with conn.cd('charm'):
            conn.run('git checkout dev',hide=True)
            conn.run('sudo ./configure.sh',hide=True,watchers=[sudopass])
            conn.run('sudo python3 setup.py install',hide=True,watchers=[sudopass])
            conn.run('pwd')
    greenletlist1 = []
    for i,h in enumerate(hosts0):
        greenlet = Greenlet(installcharm,h)
        greenlet.start()
        greenletlist1.append(greenlet)
    gevent.joinall(greenletlist1)

    def installpbc(h):
        conn = Connection(h)
        with conn.cd('pbc-0.5.14'):
            conn.run('./configure', hide=True)
            conn.run('make', hide=True)
            conn.run('sudo make install', pty=True, watchers=[sudopass], warn=True)
            conn.run('pwd')

    greenletlist0 = []
    for i, h in enumerate(hosts0):
        greenlet = Greenlet(installpbc, h)
        greenlet.start()
        greenletlist0.append(greenlet)
    gevent.joinall(greenletlist0)

def git_pull():
    hosts0 = [l for l in open('hosts', 'r').read().split('\n') if l]

    def pullHB(h):
        conn = Connection(h)
        conn.run('git clone https://github.com/JiangLaime/TinyThunder.git')
        with conn.cd('~/TinyThunder'):
            conn.run('git pull', hide=True)
            conn.run('pwd')

    greenletlist0 = []
    for i, h in enumerate(hosts0):
        greenlet = Greenlet(pullHB, h)
        greenlet.start()
        greenletlist0.append(greenlet)
    gevent.joinall(greenletlist0)

def getIP():
    return [l for l in open('hosts', 'r').read().split('\n') if l]


def idAll():
    result = []
    for region in regions:
        result += get_ec2_instances_id(region) or []
    return result


def startAll():
    for region in regions:
        start_all_instances(region)


def stopAll():
    for region in regions:
        stop_all_instances(region)

from subprocess import check_output, Popen, call, PIPE, STDOUT
# import fcntl
# from threading import Thread
# import platform


def callFabFromIPList(l, work):
    call('fab %s'  % (','.join(l), work), shell=True)

# def non_block_read(output):
#     ''' even in a thread, a normal read with block until the buffer is full '''
#     fd = output.fileno()
#     fl = fcntl.fcntl(fd, fcntl.F_GETFL)
#     fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
#     try:
#         return output.readline()
#     except:
#         return ''

# def monitor(stdout, N, t):
#     starting_time = time.time()
#     counter = 0
#     while True:
#         output = non_block_read(stdout).strip()
#         print (output)
#         if 'synced transactions set' in output:
#             counter += 1
#             if counter >= N - t:
#                 break
#     ending_time = time.time()
#     print ('Latency from client scope:', ending_time - starting_time)

def runProtocol():  # fast-path to run, assuming we already have the files ready
    callFabFromIPList(getIP(), 'runProtocol')

def runProtocolfromClient(client, key, hosts=None):
    if not hosts:
        callFabFromIPList(getIP(), 'runProtocolFromClient:%s,%s' % (client, key))
    else:
        callFabFromIPList(hosts, 'runProtocolFromClient:%s,%s' % (client, key))

def runEC2(Tx, N, t, n):  # run 4 in a row
    for i in range(1, n+1):
        runProtocolfromClient('"%d %d %d"' % (Tx, N, t), "~/%d_%d_%d.key" % (N, t, i))

def stopProtocol():
    callFabFromIPList(getIP(), 'stopProtocols')

# def callStartProtocolAndMonitorOutput(N, t, l, work='runProtocol'):
#     if platform.system() == 'Darwin':
#         popen = Popen(['fab', '-i', '~/.ssh/amiller-mc2ec2.pem',
#             '-u', 'ubuntu', '-H', ','.join(l),
#             work], stdout=PIPE, stderr=STDOUT, close_fds=True, bufsize=1, universal_newlines=True)
#     else:
#         popen = Popen('fab -i ~/.ssh/amiller-mc2ec2.pem -u ubuntu -P -H %s %s' % (','.join(l), work),
#             shell=True, stdout=PIPE, stderr=STDOUT, close_fds=True, bufsize=1, universal_newlines=True)
#     thread = Thread(target=monitor, args=[popen.stdout, N, t])
#     thread.daemon = True
#     thread.start()
#
#     popen.wait()
#     thread.join(timeout=1)
#
#     return  # to comment the following lines
#     counter = 0
#     while True:
#         line = popen.stdout.readline()
#         if not line: break
#         if 'synced transactions set' in line:
#             counter += 1
#         if counter >= N - t:
#             break
#         print (line) # yield line
#         sys.stdout.flush()
#     ending_time = time.time()
#     print ('Latency from client scope:', ending_time - starting_time)

#short-cuts

c = callFabFromIPList

if  __name__ =='__main__':
  try: __IPYTHON__
  except NameError:
    parser = argparse.ArgumentParser()
    parser.add_argument('access_key', help='Access Key');
    parser.add_argument('secret_key', help='Secret Key');
    args = parser.parse_args()
    access_key = args.access_key
    secret_key = args.secret_key
    import IPython
    IPython.embed()

