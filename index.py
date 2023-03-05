from time import time
from pickle import dump, load

class Index:
    def __init__(self):
        self.t={}
    def count(self):
        return len(self.t.keys())
    def add(self,key,val):
        self.t[key]=val
    def remove(self,key):
        self.t.pop(key)
    def find(self,key):
        return self.t.get(key)
    def printAll(self):
        for k in self.t.keys():
            print("%s -> %s" %(k, self.t[k]))
    def save(self,filename):
        self.t=dict(sorted(self.t.items()))
        f=open(filename,'wb')
        dump(self.t, f)
        f.close()
    def load(self, filename):
        f=open(filename, 'rb')
        self.t=load(f)
        f.close()

i=Index()
print ("generating :", end='')
t0=time()
for n in range(0,1000000):
    i.add("Benoit%s"%n,n)
t1=time()
print (t1-t0)

print ("save to file :", end='')
t0=time()
i.save('index_file.txt')
t1=time()
print (t1-t0)

print ("load file :", end='')
t0=time()
i.load('index_file.txt')
t1=time()
print(t1-t0)
