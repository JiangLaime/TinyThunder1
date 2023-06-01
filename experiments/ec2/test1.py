if  __name__ =='__main__':
    print(','.join([l for l in open('hosts', 'r').read().split('\n') if l]))