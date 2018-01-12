import sys
import mmap
import time, struct
import os
import numpy as np

a_offset = 0x2000
s_offset = 0x4000
u_offset = 0x6000
v_offset = 0x8000

def ipStart(mem) : 
   ## the mmap is addressed bytes by bytes, so we just cant  set a single bit. So we have to grab the whole 4-byte register . 
   packed_reg = mem[0:4]
   ## we now have 32 bits packed into a string , so to do any sort of bitwise operations with it we must unpack it.
   reg_status = struct.unpack("<L", packed_reg)[0]        ## If we will 'not' put [0] in end then it will show the error in the next operation (here next line)
   ## We now have 32-bits integer value of the register
   reg_status = reg_status & 0x80
   reg_status = reg_status | 0x01
   mem[0:4] = struct.pack("<L" , reg_status )       
   

def ipIsDone(mem) : 
    packed_reg = mem[0:4]
    reg_status = struct.unpack("<L", packed_reg)[0]
    reg_status = ((reg_status >> 1) & 0x01)
    return reg_status

def ipRestart(mem) : 
    packed_reg = mem[0:4]
    reg_status = struct.unpack("<L", packed_reg)[0]
    reg_status = reg_status ^ 0x80
    mem[0:4] = struct.pack("<L" , reg_status)


input_data = []
filename = sys.argv[1]
with open(filename) as f :
   input_data = f.readlines() ;


input_data = [x.strip(",\n") for x in input_data]
numsamples = len(input_data)

print "numsamples = " , numsamples

for i in range (0, 10):
        print (" input_data  = ") , input_data[i]

print (type(input_data[1]))


modifiedData = []

for i in range(0, numsamples):
    scaleData = int(input_data[i])
    modifiedData.append(scaleData)

modifiedData = np.asarray(modifiedData, dtype = np.uint32)
for i in range (0, 10):
        print (" modifieddata  = ") , modifiedData[i]

print (type(modifiedData[1]))

device_file = os.open("/dev/uio0", os.O_RDWR)
length = 0x10000
mem = mmap.mmap(device_file, length, mmap.MAP_SHARED, mmap.PROT_READ | mmap.PROT_WRITE, offset = 0 )
    # This will give us the mmmap range in terms of numpy array --- where each element is a 32bit
#word_array = np.frombuffer(memmap, np.uint32, length >> 2, offset = 0  )

for i in range(0, numsamples):
    data  = struct.pack("<L", int(input_data[i]))
    mem[a_offset : a_offset + 4] = data
    a_offset = a_offset + 4 
    if i <10 :
        print "a_offset = ", hex(a_offset) 

ipStart(mem)
print "IP Core has started "
while ( ipIsDone(mem) != 1) : 
     ## Do nothing 
print "IP  Core is Done "

s_output = [] 

for i in range(0, numsamples):
     packed_data = mem[s_offset : s_offset + 4]
     reg_status = struct.unpack("<L", packed_data)
     s_offset = s_offset + 4 
     s_output.append(reg_status)
     if i <10 :
        print "a_offset = ", hex(s_offset) 

u_output = []

for i in range(0, numsamples):
     packed_data = mem[u_offset : u_offset + 4]
     reg_status = struct.unpack("<L", packed_data)
     s_offset = s_offset + 4 
     s_output.append(reg_status)
     if i <10 :
        print "a_offset = ", hex(u_offset) 

v_output = []

for i in range(0, numsamples):
     packed_data = mem[v_offset : v_offset + 4]
     reg_status = struct.unpack("<L", packed_data)
     s_offset = s_offset + 4 
     v_output.append(reg_status)
     if i <10 :
        print "a_offset = ", hex(v_offset) 

file1 = open('ss.txt' , 'w')
for item in s_output:
    file1.write("%d\n" % item)

file1 = open('uu.txt' , 'w')
for item in s_output:
    file1.write("%d\n" % item)

file1 = open('vv.txt' , 'w')
for item in s_output:
    file1.write("%d\n" % item)

file1.close()
file2.close()
file3.close()
f.close()
os.close(device_file)

'''
if __name__ == "__main__" :
      import sys
      sys.exit(main())
'''


