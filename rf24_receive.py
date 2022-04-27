import RPi.GPIO as GPIO
import time
#GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

rf24_cePin = 8
rf24_csPin = 12
rf24_mosiPin = 16
rf24_misoPin = 15
rf24_clkPin = 11
rf24_status = 0

rf24_stdwait = 0.000000125    #Speed of ATTiny

def rf24_ce(lev):
    GPIO.output(rf24_cePin, lev)
    time.sleep(rf24_stdwait)

def rf24_cs(lev):
    GPIO.output(rf24_csPin, lev)
    time.sleep(rf24_stdwait)

def rf24_mosi(lev):
    if(lev):
        GPIO.output(rf24_mosiPin, 1)
    else:
        GPIO.output(rf24_mosiPin, 0)
    time.sleep(rf24_stdwait)
    
def rf24_miso():
    if(GPIO.input(rf24_misoPin)):
        return 0xFF
    else:
        return 0x00

def rf24_clk(lev):
    GPIO.output(rf24_clkPin, lev)
    time.sleep(rf24_stdwait)

def rf24_init():
    GPIO.setup(rf24_cePin, GPIO.OUT)
    GPIO.setup(rf24_csPin, GPIO.OUT)
    GPIO.setup(rf24_mosiPin, GPIO.OUT)
    GPIO.setup(rf24_misoPin, GPIO.IN)
    GPIO.setup(rf24_clkPin, GPIO.OUT)
    rf24_ce(0)
    rf24_cs(1)
    time.sleep(0.2)

def rf24_command(cmd):
    global rf24_status
    n = 128
    ret = 0
    while(n):
        if(cmd & n):
            rf24_mosi(1)
        else:
            rf24_mosi(0)
        rf24_clk(1)
        ret |= (rf24_miso() & n)
        rf24_clk(0)
        n >>= 1
    rf24_status = ret    
    return ret

def rf24_readbyte():
    n = 128
    v = 0
    while(n):
        rf24_clk(1)
        v |= (rf24_miso() & n)
        rf24_clk(0)
        n >>= 1
    return v

def rf24_writebyte(value):
    n = 128
    while(n):
        rf24_mosi(value & n)
        rf24_clk(1)
        rf24_clk(0)
        n >>= 1

def rf24_reg_read(reg):
    rx = 0
    rf24_cs(0)
    rf24_command(reg)
    rx = rf24_readbyte()
    rf24_cs(1)
    return rx

def rf24_reg_write(reg, value):
    rf24_cs(0)
    rf24_command(0x20 | reg)
    rx = rf24_writebyte(value)
    rf24_cs(1)

def rf24_setconfig(freq, speed, power):
    buf = 0
    if(speed==0):
        buf = 0b00100000
    elif(speed==1):
        buf = 0b00000000
    else:
        buf = 0b00001000
    buf |= ((power&3) << 1)
    rf24_reg_write(0x06, buf)
    rf24_reg_write(0x05, freq)
    
def rf24_setautoretransmit(delay, count):
    buf = (delay << 4) | (count & 0x0F)
    rf24_reg_write(0x04, buf)
    
def rf24_setaddress(pipe, a5, a4, a3, a2, a1):
    rf24_cs(0)
    rf24_command(0x20 | 0x0A | pipe)
    rf24_writebyte(a1)
    if(pipe<2):
        rf24_writebyte(a2)
        rf24_writebyte(a3)
        rf24_writebyte(a4)
        rf24_writebyte(a5)
    rf24_cs(1)
    if(pipe==0):
        rf24_cs(0)
        rf24_command(0x20 | 0x10)
        rf24_writebyte(a1)
        rf24_writebyte(a2)
        rf24_writebyte(a3)
        rf24_writebyte(a4)
        rf24_writebyte(a5)
        rf24_cs(1)
    

def rf24_gettxaddr():
    rf24_cs(0)
    rf24_command(0x10)
    a1 = rf24_readbyte()
    a2 = rf24_readbyte()
    a3 = rf24_readbyte()
    a4 = rf24_readbyte()
    a5 = rf24_readbyte()
    rf24_cs(1)
    return a1, a2, a3, a4, a5

def rf24_getrxaddr(pipe):
    rf24_cs(0)
    rf24_command(0x0A + pipe)
    a1 = rf24_readbyte()
    a2 = rf24_readbyte()
    a3 = rf24_readbyte()
    a4 = rf24_readbyte()
    a5 = rf24_readbyte()
    rf24_cs(1)
    return a1, a2, a3, a4, a5

def rf24_set_payload_length(l):
    for n in range(6):
        rf24_reg_write(0x11 + n, l)

def rf24_flush():
    rf24_cs(0)
    rf24_command(0b11100010) # Flush RX
    rf24_cs(1)
    rf24_cs(0)
    rf24_command(0b11100001) # Flush TX
    rf24_cs(1)

def rf24_powerup_rx():
    global rf24_status
    rf24_flush()
    rf24_reg_write(0x07, rf24_status & 0b01110000) #clear status
    rf24_reg_write(0x00, (rf24_reg_read(0x00) & 0b11111100) | 0b00000011)
    rf24_ce(1)
    time.sleep(0.005)
    
def rf24_powerup_tx():
    global rf24_status
    rf24_flush()
    rf24_reg_write(0x07, rf24_status & 0b01110000) #clear status
    rf24_reg_write(0x00, (rf24_reg_read(0x00) & 0b11111100) | 0b00000010)
    rf24_ce(1)
    time.sleep(0.005)

def rf24_powerdown():
    rf24_reg_write(0x00, rf24_reg_read(0x00) & 0b11111100)
    rf24_ce(0)

def rf24_getstatus():
    global rf24_status
    rf24_cs(0)
    rf24_command(0xFF)
    rf24_cs(1)
    return rf24_status

def rf24_dataready():
    if(rf24_getstatus() & 0b01000000):
        return 1
    if(rf24_reg_read(0x17) & 1): # RX_EMPTY
        return 0
    else:
        return 1
    
def rf24_datasent():
    return (rf24_getstatus() & 0b00100000)

def rf24_maxretry():
    return (rf24_getstatus() & 0b00010000)
    
def rf24_get_payload_length():
    l = 0
    rf24_cs(0)
    rf24_command(0b01100000)
    l = rf24_readbyte()
    rf24_cs(1)
    return l
    
def rf24_send(t):
    l = len(t)
    rf24_cs(0)
    rf24_command(0b10100000)
    for n in range(l):
        rf24_write_byte(t[n])
    rf24_cs(1)

def rf24_get_message(length):
    t = []
    rf24_cs(0)
    rf24_command(0b01100001)
    for n in range(length):
        t.append(rf24_readbyte())
    return t
        
    
    
    


try:
    print("program started.")
    rf24_init()
    rf24_setconfig(5,0,0)
    rf24_setconfig(1,0,0)
    rf24_setaddress(0, 100,100,100,100,99)
    rf24_setaddress(0, 100,100,100,100,100)
    rf24_setautoretransmit(15,15)
    rf24_set_payload_length(3)
    
    print("tx addr:",rf24_gettxaddr())
    print("tx addr P0:",rf24_getrxaddr(0))
    print("frequence:",rf24_reg_read(0x05))
    
    rf24_setconfig(2,0,0)
    rf24_setaddress(0, 100,100,100,100,100)
    
    print("start listening...")
    #rf24_powerup_rx()
    while(1):
        rf24_powerup_rx()
        loop = 1
        while(loop):
            if(rf24_dataready()):
                loop = 0
                #print("dataready!")
        t=rf24_get_message(3)
        print(t)
        rf24_reg_write(0x07, rf24_status & 0b01110000) #clear status
        #rf24_flush()
        rf24_powerdown()

        
except KeyboardInterrupt:
    GPIO.cleanup()
    print("program finished.")
