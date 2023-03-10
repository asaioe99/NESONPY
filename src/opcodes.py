# 8bit非負整数演算
def dec_uint8(a, b):
    if a >= b:
        return (a - b) & 0x00FF
    else:
        return ((a | 0x100) - b) & 0x00FF

def dec_uint8_tri(a, b, c):
    return dec_uint8(dec_uint8(a, b), c)

# 割り込み
# NMI
def nmi(cpu, mb, ppu):
    cpu.P["B"] = False
    cpu.push(mb, (cpu.PC >> 8) & 0x00FF, ppu)
    cpu.push(mb, cpu.PC & 0x00FF, ppu)
    cpu.P["1"] = True # 不要だけど実機はこう
    data = 0x00
    bitmask = 0x80
    for i in cpu.P.values():
        if i == True:
            data += bitmask
        bitmask >>= 1
    cpu.push(mb, data, ppu)
    cpu.P["1"] = False
    cpu.P["I"] = True
    cpu.PC = mb.mmu_read(0xFFFA, ppu) | mb.mmu_read(0xFFFB, ppu) << 8

# アドレッシングモード
def sim8_ads(cpu, mb, ppu):
    return mb.mmu_read(cpu.PC + 1, ppu)

def im8_ads(cpu, mb, ppu): # Zero Page
    return mb.mmu_read(cpu.PC + 1, ppu) & 0x00FF

def im8x_ads(cpu, mb, ppu): # Absolute, X
    return (mb.mmu_read(cpu.PC + 1, ppu) + cpu.X) & 0x00FF

def im8y_ads(cpu, mb, ppu): # Absolute, Y
    return (mb.mmu_read(cpu.PC + 1, ppu) + cpu.Y) & 0x00FF

def im16_ads(cpu, mb, ppu): # Absolute
    return mb.mmu_read(cpu.PC + 1, ppu) | mb.mmu_read(cpu.PC + 2, ppu) << 8

def im16x_ads(cpu, mb, ppu): # Absolute, X
    return ((mb.mmu_read(cpu.PC + 1, ppu) | mb.mmu_read(cpu.PC + 2, ppu) << 8) + cpu.X) % 0x10000

def im16y_ads(cpu, mb, ppu):# Absolute, Y
    return ((mb.mmu_read(cpu.PC + 1, ppu) | mb.mmu_read(cpu.PC + 2, ppu) << 8) + cpu.Y) % 0x10000

def iim8x_ads(cpu, mb, ppu): # (indirect, X)
    addr = (mb.mmu_read(cpu.PC + 1, ppu) + cpu.X) & 0x00FF
    if addr == 0xFF:
        addr_l = mb.mmu_read(addr, ppu)
        addr_h = mb.mmu_read(addr &0xFF00, ppu)
    else:
        addr_l = mb.mmu_read(addr, ppu)
        addr_h = mb.mmu_read(addr + 1, ppu)
    return addr_l | addr_h << 8

def iim8y_ads(cpu, mb, ppu): # (indirect), Y
    addr = mb.mmu_read(cpu.PC + 1, ppu) & 0x00FF
    if addr == 0xFF:
        addr_l = mb.mmu_read(addr, ppu)
        addr_h = mb.mmu_read(addr &0xFF00, ppu)
    else:
        addr_l = mb.mmu_read(addr, ppu)
        addr_h = mb.mmu_read(addr + 1, ppu)
    return ((addr_l | addr_h << 8) + cpu.Y) & 0xFFFF

# flag all clear
def flag_clear(cpu): # don't care なのか不明
    cpu.P['N'] = False
    cpu.P['V'] = False
    cpu.P['1'] = True
    cpu.P['B'] = False
    cpu.P['D'] = False
    cpu.P['I'] = False
    cpu.P['Z'] = False
    cpu.P['C'] = False

def set_f_zn(cpu, value): # don't care なのか不明
    cpu.P['N'] = value & 0x80 > 0
    cpu.P['Z'] = value == 0

# 転送命令
# LDA命令
def lda_sim8(cpu, mb, ppu): # 0xA9
    cpu.A = sim8_ads(cpu, mb, ppu)
    cpu.PC += 2
    set_f_zn(cpu, cpu.A)

def lda_im8(cpu, mb, ppu): # 0xA5
    addr = im8_ads(cpu, mb, ppu)
    cpu.A = mb.mmu_read(addr, ppu)
    cpu.PC += 2
    set_f_zn(cpu, cpu.A)

def lda_im8x(cpu, mb, ppu): # 0xB5
    addr = im8x_ads(cpu, mb, ppu)
    cpu.A = mb.mmu_read(addr, ppu)
    cpu.PC += 2
    set_f_zn(cpu, cpu.A)

def lda_im16(cpu, mb, ppu): # 0xAD
    addr = im16_ads(cpu, mb, ppu)
    cpu.A = mb.mmu_read(addr, ppu)
    cpu.PC += 3
    set_f_zn(cpu, cpu.A)

def lda_im16x(cpu, mb, ppu): # 0xBD
    addr = im16x_ads(cpu, mb, ppu)
    cpu.A = mb.mmu_read(addr, ppu)
    cpu.PC += 3
    set_f_zn(cpu, cpu.A)

def lda_im16y(cpu, mb, ppu): # 0xB9
    addr = im16y_ads(cpu, mb, ppu)
    cpu.A = mb.mmu_read(addr, ppu)
    cpu.PC += 3
    set_f_zn(cpu, cpu.A)

def lda_iim8x(cpu, mb, ppu): # 0xA1
    addr = iim8x_ads(cpu, mb, ppu)
    cpu.A = mb.mmu_read(addr, ppu)
    cpu.PC += 2
    set_f_zn(cpu, cpu.A)

def lda_iim8y(cpu, mb, ppu): # 0xB1
    addr = iim8y_ads(cpu, mb, ppu)
    cpu.A = mb.mmu_read(addr, ppu)
    cpu.PC += 2
    set_f_zn(cpu, cpu.A)

# LDX命令
def ldx_sim8(cpu, mb, ppu): # 0xA2
    cpu.X = sim8_ads(cpu, mb, ppu)
    cpu.PC += 2
    set_f_zn(cpu, cpu.X)

def ldx_im8(cpu, mb, ppu): # 0xA6
    addr = im8_ads(cpu, mb, ppu)
    cpu.X = mb.mmu_read(addr, ppu)
    cpu.PC += 2
    set_f_zn(cpu, cpu.X)

def ldx_im8y(cpu, mb, ppu): # 0xB6
    addr = im8y_ads(cpu, mb, ppu)
    cpu.X = mb.mmu_read(addr, ppu)
    cpu.PC += 2
    set_f_zn(cpu, cpu.X)

def ldx_im16(cpu, mb, ppu): # 0xAE
    addr = im16_ads(cpu, mb, ppu)
    cpu.X = mb.mmu_read(addr, ppu)
    cpu.PC += 3
    set_f_zn(cpu, cpu.X)

def ldx_im16y(cpu, mb, ppu): # 0xBE
    addr = im16y_ads(cpu, mb, ppu)
    cpu.X = mb.mmu_read(addr, ppu)
    cpu.PC += 3
    set_f_zn(cpu, cpu.X)

# LDY命令
def ldy_sim8(cpu, mb, ppu): # 0xA0
    cpu.Y = sim8_ads(cpu, mb, ppu)
    cpu.PC += 2
    set_f_zn(cpu, cpu.Y)

def ldy_im8(cpu, mb, ppu): # 0xA4
    addr = im8_ads(cpu, mb, ppu)
    cpu.Y = mb.mmu_read(addr, ppu)
    cpu.PC += 2
    set_f_zn(cpu, cpu.Y)

def ldy_im8x(cpu, mb, ppu): # 0xB4
    addr = im8x_ads(cpu, mb, ppu)
    cpu.Y = mb.mmu_read(addr, ppu)
    cpu.PC += 2
    set_f_zn(cpu, cpu.Y)

def ldy_im16(cpu, mb, ppu): # 0xAC
    addr = im16_ads(cpu, mb, ppu)
    cpu.Y = mb.mmu_read(addr, ppu)
    cpu.PC += 3
    set_f_zn(cpu, cpu.Y)

def ldy_im16x(cpu, mb, ppu): # 0xBC
    addr = im16x_ads(cpu, mb, ppu)
    cpu.Y = mb.mmu_read(addr, ppu)
    cpu.PC += 3
    set_f_zn(cpu, cpu.Y)

# STA命令
def sta_im8(cpu, mb, ppu): # 0x85
    addr = im8_ads(cpu, mb, ppu)
    mb.mmu_write(addr, cpu.A, ppu)
    cpu.PC += 2

def sta_im8x(cpu, mb, ppu): # 0x95
    addr = im8x_ads(cpu, mb, ppu)
    mb.mmu_write(addr, cpu.A, ppu)
    cpu.PC += 2

def sta_im16(cpu, mb, ppu): # 0x8D
    addr = im16_ads(cpu, mb, ppu)
    mb.mmu_write(addr, cpu.A, ppu)
    cpu.PC += 3

def sta_im16x(cpu, mb, ppu): # 0x9D
    addr = im16x_ads(cpu, mb, ppu)
    mb.mmu_write(addr, cpu.A, ppu)
    cpu.PC += 3

def sta_im16y(cpu, mb, ppu): # 0x99
    addr = im16y_ads(cpu, mb, ppu)
    mb.mmu_write(addr, cpu.A, ppu)
    cpu.PC += 3

def sta_iim8x(cpu, mb, ppu): # 0x81
    addr = iim8x_ads(cpu, mb, ppu)
    mb.mmu_write(addr, cpu.A, ppu)
    cpu.PC += 2

def sta_iim8y(cpu, mb, ppu): # 0x91
    addr = iim8y_ads(cpu, mb, ppu)
    mb.mmu_write(addr, cpu.A, ppu)
    cpu.PC += 2

# STX命令
def stx_im8(cpu, mb, ppu): # 0x86
    addr = im8_ads(cpu, mb, ppu)
    mb.mmu_write(addr, cpu.X, ppu)
    cpu.PC += 2

def stx_im8y(cpu, mb, ppu): # 0x96
    addr = im8y_ads(cpu, mb, ppu)
    mb.mmu_write(addr, cpu.X, ppu)
    cpu.PC += 2

def stx_im16(cpu, mb, ppu): # 0x8E
    addr = im16_ads(cpu, mb, ppu)
    mb.mmu_write(addr, cpu.X, ppu)
    cpu.PC += 3

# STY命令
def sty_im8(cpu, mb, ppu): # 0x84
    addr = im8_ads(cpu, mb, ppu)
    mb.mmu_write(addr, cpu.Y, ppu)
    cpu.PC += 2

def sty_im8x(cpu, mb, ppu): # 0x94
    addr = im8x_ads(cpu, mb, ppu)
    mb.mmu_write(addr, cpu.Y, ppu)
    cpu.PC += 2

def sty_im16(cpu, mb, ppu): # 0x8C
    addr = im16_ads(cpu, mb, ppu)
    mb.mmu_write(addr, cpu.Y, ppu)
    cpu.PC += 3

# TAX命令
def tax(cpu, mb): # 0xAA
    cpu.X = cpu.A
    cpu.PC += 1
    set_f_zn(cpu, cpu.X)

# TAY命令
def tay(cpu, mb): # 0xA8
    cpu.Y = cpu.A
    cpu.PC += 1
    set_f_zn(cpu, cpu.Y)

# TSX命令
def tsx(cpu, mb): # 0xBA
    cpu.X = cpu.SP & 0x00FF
    cpu.PC += 1
    set_f_zn(cpu, cpu.X)

# TXA命令
def txa(cpu, mb): # 0x8A
    cpu.A = cpu.X
    cpu.PC += 1
    set_f_zn(cpu, cpu.A)

# TXS命令
def txs(cpu, mb): # 0x9A
    cpu.SP = cpu.X | 0x0100
    cpu.PC += 1
    #set_f_zn(cpu, cpu.SP)

# TYA命令
def tya(cpu, mb): # 0x98
    cpu.A = cpu.Y
    cpu.PC += 1
    set_f_zn(cpu, cpu.A)

# 算術命令
# ADC命令
def adc_sim8(cpu, mb, ppu): # 0x69
    data = sim8_ads(cpu, mb, ppu)
    value = cpu.A + data + int(cpu.P['C'])
    cpu.P['C'] = (value & 0x100) > 0
    cpu.P['V'] = (((cpu.A ^ value) & (data ^ value)) & 0x80) > 0
    cpu.A = value & 0x00FF
    set_f_zn(cpu, cpu.A)
    cpu.PC += 2

def adc_im8(cpu, mb, ppu): # 0x65
    addr = im8_ads(cpu, mb, ppu)
    value = (cpu.A + mb.mmu_read(addr, ppu) + int(cpu.P['C']))
    cpu.P['V'] = (((cpu.A ^ value) & (mb.mmu_read(addr, ppu) ^ value)) & 0x80) > 0
    cpu.P['C'] = (value & 0x100) > 0
    cpu.A = value & 0x00FF
    set_f_zn(cpu, cpu.A)
    cpu.PC += 2

def adc_im8x(cpu, mb, ppu): # 0x75
    addr = im8x_ads(cpu, mb, ppu)
    value = (cpu.A + mb.mmu_read(addr, ppu) + int(cpu.P['C']))
    cpu.P['V'] = (((cpu.A ^ value) & (mb.mmu_read(addr, ppu) ^ value)) & 0x80) > 0
    cpu.P['C'] = (value & 0x100) > 0
    cpu.A = value & 0x00FF
    set_f_zn(cpu, cpu.A)
    cpu.PC += 2

def adc_im16(cpu, mb, ppu): # 0x6D
    addr = im16_ads(cpu, mb, ppu)
    value = (cpu.A + mb.mmu_read(addr, ppu) + int(cpu.P['C']))
    cpu.P['V'] = (((cpu.A ^ value) & (mb.mmu_read(addr, ppu) ^ value)) & 0x80) > 0
    cpu.P['C'] = (value & 0x100) > 0
    cpu.A = value & 0x00FF
    set_f_zn(cpu, cpu.A)
    cpu.PC += 3

def adc_im16x(cpu, mb, ppu): # 0x7D
    addr = im16x_ads(cpu, mb, ppu)
    value = (cpu.A + mb.mmu_read(addr, ppu) + int(cpu.P['C']))
    cpu.P['V'] = (((cpu.A ^ value) & (mb.mmu_read(addr, ppu) ^ value)) & 0x80) > 0
    cpu.P['C'] = (value & 0x100) > 0
    cpu.A = value & 0x00FF
    set_f_zn(cpu, cpu.A)
    cpu.PC += 3

def adc_im16y(cpu, mb, ppu): # 0x79
    addr = im16y_ads(cpu, mb, ppu)
    value = (cpu.A + mb.mmu_read(addr, ppu) + int(cpu.P['C']))
    cpu.P['V'] = (((cpu.A ^ value) & (mb.mmu_read(addr, ppu) ^ value)) & 0x80) > 0
    cpu.P['C'] = (value & 0x100) > 0
    cpu.A = value & 0x00FF
    set_f_zn(cpu, cpu.A)
    cpu.PC += 3

def adc_iim8x(cpu, mb, ppu): # 0x61
    addr = iim8x_ads(cpu, mb, ppu)
    value = (cpu.A + mb.mmu_read(addr, ppu) + int(cpu.P['C']))
    cpu.P['V'] = (((cpu.A ^ value) & (mb.mmu_read(addr, ppu) ^ value)) & 0x80) > 0
    cpu.P['C'] = (value & 0x100) > 0
    cpu.A = value & 0x00FF
    set_f_zn(cpu, cpu.A)
    cpu.PC += 2

def adc_iim8y(cpu, mb, ppu): # 0x71
    addr = iim8y_ads(cpu, mb, ppu)
    value = (cpu.A + mb.mmu_read(addr, ppu) + int(cpu.P['C']))
    cpu.P['V'] = (((cpu.A ^ value) & (mb.mmu_read(addr, ppu) ^ value)) & 0x80) > 0
    cpu.P['C'] = (value & 0x100) > 0
    cpu.A = value & 0x00FF
    set_f_zn(cpu, cpu.A)
    cpu.PC += 2

# ADC命令
def and_sim8(cpu, mb, ppu): # 0x29
    cpu.A &= sim8_ads(cpu, mb, ppu)
    set_f_zn(cpu, cpu.A)
    cpu.PC += 2

def and_im8(cpu, mb, ppu): # 0x25
    addr = im8_ads(cpu, mb, ppu)
    cpu.A &= mb.mmu_read(addr, ppu)
    set_f_zn(cpu, cpu.A)
    cpu.PC += 2

def and_im8x(cpu, mb, ppu): # 0x35
    addr = im8x_ads(cpu, mb, ppu)
    cpu.A &= mb.mmu_read(addr, ppu)
    set_f_zn(cpu, cpu.A)
    cpu.PC += 2

def and_im16(cpu, mb, ppu): # 0x2D
    addr = im16_ads(cpu, mb, ppu)
    cpu.A &= mb.mmu_read(addr, ppu)
    set_f_zn(cpu, cpu.A)
    cpu.PC += 3

def and_im16x(cpu, mb, ppu): # 0x3D
    addr = im16x_ads(cpu, mb, ppu)
    cpu.A &= mb.mmu_read(addr, ppu)
    set_f_zn(cpu, cpu.A)
    cpu.PC += 3

def and_im16y(cpu, mb, ppu): # 0x39
    addr = im16y_ads(cpu, mb, ppu)
    cpu.A &= mb.mmu_read(addr, ppu)
    set_f_zn(cpu, cpu.A)
    cpu.PC += 3

def and_iim8x(cpu, mb, ppu): # 0x21
    addr = iim8x_ads(cpu, mb, ppu)
    cpu.A &= mb.mmu_read(addr, ppu)
    set_f_zn(cpu, cpu.A)
    cpu.PC += 2

def and_iim8y(cpu, mb, ppu): # 0x31
    addr = iim8y_ads(cpu, mb, ppu)
    cpu.A &= mb.mmu_read(addr, ppu)
    set_f_zn(cpu, cpu.A)
    cpu.PC += 2

# ASL命令
def asl_acc(cpu, mb): # 0x0A
    cpu.P['C'] = (cpu.A & 0x80) > 0
    cpu.A <<= 1
    cpu.A &= 0x00FF
    set_f_zn(cpu, cpu.A)
    cpu.PC += 1

def asl_im8(cpu, mb, ppu): # 0x06
    addr = im8_ads(cpu, mb, ppu)
    value = mb.mmu_read(addr, ppu)
    cpu.P['C'] = (value & 0x80) > 0
    value <<= 1
    value = value & 0x00FF
    mb.mmu_write(addr, value, ppu)
    set_f_zn(cpu, value)
    cpu.PC += 2

def asl_im8x(cpu, mb, ppu): # 0x16
    addr = im8x_ads(cpu, mb, ppu)
    value = mb.mmu_read(addr, ppu)
    cpu.P['C'] = (value & 0x80) > 0
    value <<= 1
    value = value & 0x00FF
    mb.mmu_write(addr, value, ppu)
    set_f_zn(cpu, value)
    cpu.PC += 2

def asl_im16(cpu, mb, ppu): # 0x0E
    addr = im16_ads(cpu, mb, ppu)
    value = mb.mmu_read(addr, ppu)
    cpu.P['C'] = (value & 0x80) > 0
    value <<= 1
    value = value & 0x00FF
    mb.mmu_write(addr, value, ppu)
    set_f_zn(cpu, value)
    cpu.PC += 3

def asl_im16x(cpu, mb, ppu): # 0x1E
    addr = im16x_ads(cpu, mb, ppu)
    value = mb.mmu_read(addr, ppu)
    cpu.P['C'] = (value & 0x80) > 0
    value <<= 1
    value = value & 0x00FF
    mb.mmu_write(addr, value, ppu)
    set_f_zn(cpu, value)
    cpu.PC += 3

# BIT命令
def bit_im8(cpu, mb, ppu): # 0x24
    addr = im8_ads(cpu, mb, ppu)
    value = mb.mmu_read(addr, ppu)
    cpu.P['N'] = (value & 0x80) > 0
    cpu.P['V'] = (value & 0x40) > 0
    cpu.P['Z'] = (value & cpu.A) == 0
    cpu.PC += 2

def bit_im16(cpu, mb, ppu): # 0x2C
    addr = im16_ads(cpu, mb, ppu)
    value = mb.mmu_read(addr, ppu)
    cpu.P['N'] = (value & 0x80) > 0
    cpu.P['V'] = (value & 0x40) > 0
    cpu.P['Z'] = (value & cpu.A) == 0
    cpu.PC += 3

# CMP命令
def cmp_sim8(cpu, mb, ppu): # 0xC9
    data = sim8_ads(cpu, mb, ppu)
    diff = dec_uint8(cpu.A, data)
    set_f_zn(cpu, diff)
    cpu.P['C'] = not (cpu.A < data) 
    cpu.PC += 2

def cmp_im8(cpu, mb, ppu): # 0xC5
    addr = im8_ads(cpu, mb, ppu)
    data = mb.mmu_read(addr, ppu)
    diff = dec_uint8(cpu.A, data)
    set_f_zn(cpu, diff)
    cpu.P['C'] = not (cpu.A < data) 
    cpu.PC += 2

def cmp_im8x(cpu, mb, ppu): # 0xD5
    addr = im8x_ads(cpu, mb, ppu)
    data = mb.mmu_read(addr, ppu)
    diff = dec_uint8(cpu.A, data)
    set_f_zn(cpu, diff)
    cpu.P['C'] = not (cpu.A < data) 
    cpu.PC += 2

def cmp_im16(cpu, mb, ppu): # 0xCD
    addr = im16_ads(cpu, mb, ppu)
    data = mb.mmu_read(addr, ppu)
    diff = dec_uint8(cpu.A, data)
    set_f_zn(cpu, diff)
    cpu.P['C'] = not (cpu.A < data) 
    cpu.PC += 3

def cmp_im16x(cpu, mb, ppu): # 0xDD
    addr = im16x_ads(cpu, mb, ppu)
    data = mb.mmu_read(addr, ppu)
    diff = dec_uint8(cpu.A, data)
    set_f_zn(cpu, diff)
    cpu.P['C'] = not (cpu.A < data) 
    cpu.PC += 3

def cmp_im16y(cpu, mb, ppu): # 0xD9
    addr = im16y_ads(cpu, mb, ppu)
    data = mb.mmu_read(addr, ppu)
    diff = dec_uint8(cpu.A, data)
    set_f_zn(cpu, diff)
    cpu.P['C'] = not (cpu.A < data) 
    cpu.PC += 3

def cmp_iim8x(cpu, mb, ppu): # 0xC1
    addr = iim8x_ads(cpu, mb, ppu)
    data = mb.mmu_read(addr, ppu)
    diff = dec_uint8(cpu.A, data)
    set_f_zn(cpu, diff)
    cpu.P['C'] = not (cpu.A < data) 
    cpu.PC += 2

def cmp_iim8y(cpu, mb, ppu): # 0xD1
    addr = iim8y_ads(cpu, mb, ppu)
    data = mb.mmu_read(addr, ppu)
    diff = dec_uint8(cpu.A, data)
    set_f_zn(cpu, diff)
    cpu.P['C'] = not (cpu.A < data) 
    cpu.PC += 2

# CPX命令
def cpx_sim8(cpu, mb, ppu): # 0xE0
    data = sim8_ads(cpu, mb, ppu)
    diff = dec_uint8(cpu.X, data)
    set_f_zn(cpu, diff)
    cpu.P['C'] = not (cpu.X < data)
    cpu.PC += 2

def cpx_im8(cpu, mb, ppu): # 0xE4
    addr = im8_ads(cpu, mb, ppu)
    data = mb.mmu_read(addr, ppu)
    diff = dec_uint8(cpu.X, data)
    set_f_zn(cpu, diff)
    cpu.P['C'] = not (cpu.X < data)
    cpu.PC += 2

def cpx_im16(cpu, mb, ppu): # 0xEC
    addr = im16_ads(cpu, mb, ppu)
    data = mb.mmu_read(addr, ppu)
    diff = dec_uint8(cpu.X, data)
    set_f_zn(cpu, diff)
    cpu.P['C'] = not (cpu.X < data)
    cpu.PC += 3

# CPY命令
def cpy_sim8(cpu, mb, ppu): # 0xC0
    data = sim8_ads(cpu, mb, ppu)
    diff = dec_uint8(cpu.Y, data)
    set_f_zn(cpu, diff)
    cpu.P['C'] = not (cpu.Y < data)
    cpu.PC += 2

def cpy_im8(cpu, mb, ppu): # 0xC4
    addr = im8_ads(cpu, mb, ppu)
    data = mb.mmu_read(addr, ppu)
    diff = dec_uint8(cpu.Y, data)
    set_f_zn(cpu, diff)
    cpu.P['C'] = not (cpu.Y < data)
    cpu.PC += 2

def cpy_im16(cpu, mb, ppu): # 0xCC
    addr = im16_ads(cpu, mb, ppu)
    data = mb.mmu_read(addr, ppu)
    diff = dec_uint8(cpu.Y, data)
    set_f_zn(cpu, diff)
    cpu.P['C'] = not (cpu.Y < data)
    cpu.PC += 3

# DEC命令
def dec_im8(cpu, mb, ppu): # 0xC6
    addr = im8_ads(cpu, mb, ppu)
    value = dec_uint8(mb.mmu_read(addr, ppu), 1)
    mb.mmu_write(addr, value, ppu)
    set_f_zn(cpu, value)
    cpu.PC += 2

def dec_im8x(cpu, mb, ppu): # 0xD6
    addr = im8x_ads(cpu, mb, ppu)
    value = dec_uint8(mb.mmu_read(addr, ppu), 1)
    mb.mmu_write(addr, value, ppu)
    set_f_zn(cpu, value)
    cpu.PC += 2

def dec_im16(cpu, mb, ppu): # 0xCE
    addr = im16_ads(cpu, mb, ppu)
    value = dec_uint8(mb.mmu_read(addr, ppu), 1)
    mb.mmu_write(addr, value, ppu)
    set_f_zn(cpu, value)
    cpu.PC += 3

def dec_im16x(cpu, mb, ppu): # 0xDE
    addr = im16x_ads(cpu, mb, ppu)
    value = dec_uint8(mb.mmu_read(addr, ppu), 1)
    mb.mmu_write(addr, value, ppu)
    set_f_zn(cpu, value)
    cpu.PC += 3

# DEX命令
def dex(cpu, mb): # 0xCA
    cpu.X = dec_uint8(cpu.X, 1)
    cpu.PC += 1
    set_f_zn(cpu, cpu.X)

# DEY命令
def dey(cpu, mb): # 0x88
    cpu.Y = dec_uint8(cpu.Y, 1)
    cpu.PC += 1
    set_f_zn(cpu, cpu.Y)

# EOR命令
def eor_sim8(cpu, mb, ppu): # 0x49
    cpu.A ^= sim8_ads(cpu, mb, ppu)
    set_f_zn(cpu, cpu.A)
    cpu.PC += 2

def eor_im8(cpu, mb, ppu): # 0x45
    addr = im8_ads(cpu, mb, ppu)
    cpu.A ^= mb.mmu_read(addr, ppu)
    set_f_zn(cpu, cpu.A)
    cpu.PC += 2

def eor_im8x(cpu, mb, ppu): # 0x55
    addr = im8x_ads(cpu, mb, ppu)
    cpu.A ^= mb.mmu_read(addr, ppu)
    set_f_zn(cpu, cpu.A)
    cpu.PC += 2

def eor_im16(cpu, mb, ppu): # 0x4D
    addr = im16_ads(cpu, mb, ppu)
    cpu.A ^= mb.mmu_read(addr, ppu)
    set_f_zn(cpu, cpu.A)
    cpu.PC += 3

def eor_im16x(cpu, mb, ppu): # 0x4D
    addr = im16x_ads(cpu, mb, ppu)
    cpu.A ^= mb.mmu_read(addr, ppu)
    set_f_zn(cpu, cpu.A)
    cpu.PC += 3

def eor_im16y(cpu, mb, ppu): # 0x4D
    addr = im16y_ads(cpu, mb, ppu)
    cpu.A ^= mb.mmu_read(addr, ppu)
    set_f_zn(cpu, cpu.A)
    cpu.PC += 3

def eor_iim8x(cpu, mb, ppu): # 0x41
    addr = iim8x_ads(cpu, mb, ppu)
    cpu.A ^= mb.mmu_read(addr, ppu)
    set_f_zn(cpu, cpu.A)
    cpu.PC += 2

def eor_iim8y(cpu, mb, ppu): # 0x51
    addr = iim8y_ads(cpu, mb, ppu)
    cpu.A ^= mb.mmu_read(addr, ppu)
    set_f_zn(cpu, cpu.A)
    cpu.PC += 2

# INC命令
def inc_im8(cpu, mb, ppu): # 0xE6
    addr = im8_ads(cpu, mb, ppu)
    value = (mb.mmu_read(addr, ppu) + 1) & 0x00FF
    mb.mmu_write(addr, value, ppu)
    set_f_zn(cpu, value)
    cpu.PC += 2

def inc_im8x(cpu, mb, ppu): # 0xF6
    addr = im8x_ads(cpu, mb, ppu)
    value = (mb.mmu_read(addr, ppu) + 1) & 0x00FF
    mb.mmu_write(addr, value, ppu)
    set_f_zn(cpu, value)
    cpu.PC += 2

def inc_im16(cpu, mb, ppu): # 0xEE
    addr = im16_ads(cpu, mb, ppu)
    value = (mb.mmu_read(addr, ppu) + 1) & 0x00FF
    mb.mmu_write(addr, value, ppu)
    set_f_zn(cpu, value)
    cpu.PC += 3

def inc_im16x(cpu, mb, ppu): # 0xFE
    addr = im16x_ads(cpu, mb, ppu)
    value = (mb.mmu_read(addr, ppu) + 1) & 0x00FF
    mb.mmu_write(addr, value, ppu)
    set_f_zn(cpu, value)
    cpu.PC += 3

# INX命令
def inx(cpu, mb): # 0xE8
    cpu.X = (cpu.X + 1) & 0x00FF
    cpu.PC += 1
    set_f_zn(cpu, cpu.X)

# INY命令
def iny(cpu, mb): # 0xC8
    cpu.Y = (cpu.Y + 1) & 0x00FF
    cpu.PC += 1
    set_f_zn(cpu, cpu.Y)

# LSR命令
def lsr_acc(cpu, mb): # 0x4A
    cpu.P['C'] = (cpu.A & 0x01) > 0
    cpu.A >>= 1
    set_f_zn(cpu, cpu.A)
    cpu.PC += 1

def lsr_im8(cpu, mb, ppu): # 0x46
    addr = im8_ads(cpu, mb, ppu)
    value = mb.mmu_read(addr, ppu)
    cpu.P['C'] = (value & 0x01) > 0
    value >>= 1
    mb.mmu_write(addr, value, ppu)
    set_f_zn(cpu, value)
    cpu.PC += 2

def lsr_im8x(cpu, mb, ppu): # 0x56
    addr = im8x_ads(cpu, mb, ppu)
    value = mb.mmu_read(addr, ppu)
    cpu.P['C'] = (value & 0x01) > 0
    value >>= 1
    mb.mmu_write(addr, value, ppu)
    set_f_zn(cpu, value)
    cpu.PC += 2

def lsr_im16(cpu, mb, ppu): # 0x4E
    addr = im16_ads(cpu, mb, ppu)
    value = mb.mmu_read(addr, ppu)
    cpu.P['C'] = (value & 0x01) > 0
    value >>= 1
    mb.mmu_write(addr, value, ppu)
    set_f_zn(cpu, value)
    cpu.PC += 3

def lsr_im16x(cpu, mb, ppu): # 0x5E
    addr = im16x_ads(cpu, mb, ppu)
    value = mb.mmu_read(addr, ppu)
    cpu.P['C'] = (value & 0x01) > 0
    value >>= 1
    mb.mmu_write(addr, value, ppu)
    set_f_zn(cpu, value)
    cpu.PC += 3

# ORA命令
def ora_sim8(cpu, mb, ppu): # 0x09
    cpu.A |= sim8_ads(cpu, mb, ppu)
    set_f_zn(cpu, cpu.A)
    cpu.PC += 2

def ora_im8(cpu, mb, ppu): # 0x05
    addr = im8_ads(cpu, mb, ppu)
    cpu.A |= mb.mmu_read(addr, ppu)
    set_f_zn(cpu, cpu.A)
    cpu.PC += 2

def ora_im8x(cpu, mb, ppu): # 0x15
    addr = im8x_ads(cpu, mb, ppu)
    cpu.A |= mb.mmu_read(addr, ppu)
    set_f_zn(cpu, cpu.A)
    cpu.PC += 2

def ora_im16(cpu, mb, ppu): # 0x0D
    addr = im16_ads(cpu, mb, ppu)
    cpu.A |= mb.mmu_read(addr, ppu)
    set_f_zn(cpu, cpu.A)
    cpu.PC += 3

def ora_im16x(cpu, mb, ppu): # 0x1D
    addr = im16x_ads(cpu, mb, ppu)
    cpu.A |= mb.mmu_read(addr, ppu)
    set_f_zn(cpu, cpu.A)
    cpu.PC += 3

def ora_im16y(cpu, mb, ppu): # 0x19
    addr = im16y_ads(cpu, mb, ppu)
    cpu.A |= mb.mmu_read(addr, ppu)
    set_f_zn(cpu, cpu.A)
    cpu.PC += 3

def ora_iim8x(cpu, mb, ppu): # 0x01
    addr = iim8x_ads(cpu, mb, ppu)
    cpu.A |= mb.mmu_read(addr, ppu)
    set_f_zn(cpu, cpu.A)
    cpu.PC += 2

def ora_iim8y(cpu, mb, ppu): # 0x11
    addr = iim8y_ads(cpu, mb, ppu)
    cpu.A |= mb.mmu_read(addr, ppu)
    set_f_zn(cpu, cpu.A)
    cpu.PC += 2

# ROL命令
def rol_acc(cpu, mb): # 0x2A
    ogn_c = cpu.P['C'] > 0
    cpu.P['C'] = (cpu.A & 0x80) > 0
    cpu.A <<= 1
    cpu.A &= 0x00FF
    if ogn_c:
        cpu.A |= 0x01
    set_f_zn(cpu, cpu.A)
    cpu.PC += 1

def rol_im8(cpu, mb, ppu): # 0x26
    addr = im8_ads(cpu, mb, ppu)
    value = mb.mmu_read(addr, ppu)
    ogn_c = cpu.P['C'] > 0
    cpu.P['C'] = (value & 0x80) > 0
    value <<= 1
    value = value & 0x00FF
    if ogn_c:
        value |= 0x01
    mb.mmu_write(addr, value, ppu)
    set_f_zn(cpu, value)
    cpu.PC += 2

def rol_im8x(cpu, mb, ppu): # 0x36
    addr = im8x_ads(cpu, mb, ppu)
    value = mb.mmu_read(addr, ppu)
    ogn_c = cpu.P['C'] > 0
    cpu.P['C'] = (value & 0x80) > 0
    value <<= 1
    value = value & 0x00FF
    if ogn_c:
        value |= 0x01
    mb.mmu_write(addr, value, ppu)
    set_f_zn(cpu, value)
    cpu.PC += 2

def rol_im16(cpu, mb, ppu): # 0x2E
    addr = im16_ads(cpu, mb, ppu)
    value = mb.mmu_read(addr, ppu)
    ogn_c = cpu.P['C'] > 0
    cpu.P['C'] = (value & 0x80) > 0
    value <<= 1
    value = value & 0x00FF
    if ogn_c:
        value |= 0x01
    mb.mmu_write(addr, value, ppu)
    set_f_zn(cpu, value)
    cpu.PC += 3

def rol_im16x(cpu, mb, ppu): # 0x3E
    addr = im16x_ads(cpu, mb, ppu)
    value = mb.mmu_read(addr, ppu)
    ogn_c = cpu.P['C'] > 0
    cpu.P['C'] = (value & 0x80) > 0
    value <<= 1
    value = value & 0x00FF
    if ogn_c:
        value |= 0x01
    mb.mmu_write(addr, value, ppu)
    set_f_zn(cpu, value)
    cpu.PC += 3

# ROR命令
def ror_acc(cpu, mb): # 0x6A
    ogn_c = cpu.P['C'] > 0
    cpu.P['C'] = (cpu.A & 0x01) > 0
    cpu.A >>= 1
    cpu.A &= 0x00FF
    if ogn_c:
        cpu.A |= 0x80
    set_f_zn(cpu, cpu.A)
    cpu.PC += 1

def ror_im8(cpu, mb, ppu): # 0x26
    addr = im8_ads(cpu, mb, ppu)
    value = mb.mmu_read(addr, ppu)
    ogn_c = cpu.P['C'] > 0
    cpu.P['C'] = (value & 0x01) > 0
    value >>= 1
    value = value & 0x00FF
    if ogn_c:
        value |= 0x80
    mb.mmu_write(addr, value, ppu)
    set_f_zn(cpu, value)
    cpu.PC += 2

def ror_im8x(cpu, mb, ppu): # 0x76
    addr = im8x_ads(cpu, mb, ppu)
    value = mb.mmu_read(addr, ppu)
    ogn_c = cpu.P['C'] > 0
    cpu.P['C'] = (value & 0x01) > 0
    value >>= 1
    value = value & 0x00FF
    if ogn_c:
        value |= 0x80
    mb.mmu_write(addr, value, ppu)
    set_f_zn(cpu, value)
    cpu.PC += 2

def ror_im16(cpu, mb, ppu): # 0x6E
    addr = im16_ads(cpu, mb, ppu)
    value = mb.mmu_read(addr, ppu)
    ogn_c = cpu.P['C'] > 0
    cpu.P['C'] = (value & 0x01) > 0
    value >>= 1
    value = value & 0x00FF
    if ogn_c:
        value |= 0x80
    mb.mmu_write(addr, value, ppu)
    set_f_zn(cpu, value)
    cpu.PC += 3

def ror_im16x(cpu, mb, ppu): # 0x7E
    addr = im16x_ads(cpu, mb, ppu)
    value = mb.mmu_read(addr, ppu)
    ogn_c = cpu.P['C'] > 0
    cpu.P['C'] = (value & 0x01) > 0
    value >>= 1
    value = value & 0x00FF
    if ogn_c:
        value |= 0x80
    mb.mmu_write(addr, value, ppu)
    set_f_zn(cpu, value)
    cpu.PC += 3

# SBC命令
def sbc_sim8(cpu, mb, ppu): # 0xE9
    data = sim8_ads(cpu, mb, ppu)
    value = dec_uint8_tri(cpu.A, data, int(not cpu.P['C']))
    cpu.P['V'] = (((cpu.A ^ value) & (((~data) & 0xFF) ^ value)) & 0x80) > 0
    cpu.P['C'] = not (cpu.A < (data + int(not cpu.P['C'])))
    cpu.A = value
    set_f_zn(cpu, cpu.A)
    cpu.PC += 2

def sbc_im8(cpu, mb, ppu): # 0xE5
    addr = im8_ads(cpu, mb, ppu)
    data = mb.mmu_read(addr, ppu)
    value = dec_uint8_tri(cpu.A, data, int(not cpu.P['C']))
    cpu.P['V'] = (((cpu.A ^ value) & (((~data) & 0xFF) ^ value)) & 0x80) > 0
    cpu.P['C'] = not (cpu.A < (data + int(not cpu.P['C'])))
    cpu.A = value
    set_f_zn(cpu, cpu.A)
    cpu.PC += 2

def sbc_im8x(cpu, mb, ppu): # 0xF5
    addr = im8x_ads(cpu, mb, ppu)
    data = mb.mmu_read(addr, ppu)
    value = dec_uint8_tri(cpu.A, data, int(not cpu.P['C']))
    cpu.P['V'] = (((cpu.A ^ value) & (((~data) & 0xFF) ^ value)) & 0x80) > 0
    cpu.P['C'] = not (cpu.A < (data + int(not cpu.P['C'])))
    cpu.A = value
    set_f_zn(cpu, cpu.A)
    cpu.PC += 2

def sbc_im16(cpu, mb, ppu): # 0xED
    addr = im16_ads(cpu, mb, ppu)
    data = mb.mmu_read(addr, ppu)
    value = dec_uint8_tri(cpu.A, data, int(not cpu.P['C']))
    cpu.P['V'] = (((cpu.A ^ value) & (((~data) & 0xFF) ^ value)) & 0x80) > 0
    cpu.P['C'] = not (cpu.A < (data + int(not cpu.P['C'])))
    cpu.A = value
    set_f_zn(cpu, cpu.A)
    cpu.PC += 3

def sbc_im16x(cpu, mb, ppu): # 0xFD
    addr = im16x_ads(cpu, mb, ppu)
    data = mb.mmu_read(addr, ppu)
    value = dec_uint8_tri(cpu.A, data, int(not cpu.P['C']))
    cpu.P['V'] = (((cpu.A ^ value) & (((~data) & 0xFF) ^ value)) & 0x80) > 0
    cpu.P['C'] = not (cpu.A < (data + int(not cpu.P['C'])))
    cpu.A = value
    set_f_zn(cpu, cpu.A)
    cpu.PC += 3

def sbc_im16y(cpu, mb, ppu): # 0xF9
    addr = im16y_ads(cpu, mb, ppu)
    data = mb.mmu_read(addr, ppu)
    value = dec_uint8_tri(cpu.A, data, int(not cpu.P['C']))
    cpu.P['V'] = (((cpu.A ^ value) & (((~data) & 0xFF) ^ value)) & 0x80) > 0
    cpu.P['C'] = not (cpu.A < (data + int(not cpu.P['C'])))
    cpu.A = value & 0x00FF
    set_f_zn(cpu, cpu.A)
    cpu.PC += 3

def sbc_iim8x(cpu, mb, ppu): # 0xE1
    addr = iim8x_ads(cpu, mb, ppu)
    data = mb.mmu_read(addr, ppu)
    value = dec_uint8_tri(cpu.A, data, int(not cpu.P['C']))
    cpu.P['V'] = (((cpu.A ^ value) & (((~data) & 0xFF) ^ value)) & 0x80) > 0
    #cpu.P['C'] = not ((value & 0x100) > 0)
    cpu.P['C'] = not (cpu.A < (data + int(not cpu.P['C'])))
    cpu.A = value & 0x00FF
    set_f_zn(cpu, cpu.A)
    cpu.PC += 2

def sbc_iim8y(cpu, mb, ppu): # 0xF1
    addr = iim8y_ads(cpu, mb, ppu)
    data = mb.mmu_read(addr, ppu)
    value = dec_uint8_tri(cpu.A, data, int(not cpu.P['C']))
    cpu.P['V'] = (((cpu.A ^ value) & (((~data) & 0xFF) ^ value)) & 0x80) > 0
    #cpu.P['C'] = not ((value & 0x100) > 0)
    cpu.P['C'] = not (cpu.A < (data + int(not cpu.P['C'])))
    cpu.A = value
    set_f_zn(cpu, cpu.A)
    cpu.PC += 2

# スタック命令
# PHA命令
def pha(cpu, mb, ppu): # 0x48
    cpu.push(mb, cpu.A, ppu)
    cpu.PC += 1

# PHP命令
def php(cpu, mb, ppu): # 0x08
    data = 0x00
    bitmask = 0x80
    for i in cpu.P.values():
        if i == True:
            data |= bitmask
        bitmask >>= 1
    cpu.push(mb, data, ppu)
    #print("data:" + str(format(data , '02X')))
    cpu.PC += 1

# PLA命令
def pla(cpu, mb, ppu): # 0x68
    cpu.SP += 1
    cpu.A = mb.mmu_read(0x100 | cpu.SP, ppu)
    set_f_zn(cpu, cpu.A)
    cpu.PC += 1

# PLP命令
def plp(cpu, mb, ppu): # 0x28
    cpu.SP += 1
    value = mb.mmu_read(0x100 | cpu.SP, ppu)
    cpu.P["N"] = (value & 0x80) > 0
    cpu.P["V"] = (value & 0x40) > 0
    cpu.P["1"] = True # (value & 0x20) > 0
    cpu.P["B"] = (value & 0x10) > 0
    cpu.P["D"] = (value & 0x08) > 0
    cpu.P["I"] = (value & 0x04) > 0
    cpu.P["Z"] = (value & 0x02) > 0
    cpu.P["C"] = (value & 0x01) > 0
    cpu.PC += 1

# ジャンプ命令
# JMP命令
def jmp_im16(cpu, mb, ppu): # 0x4C
    addr = im16_ads(cpu, mb, ppu)
    cpu.PC = addr #mb.mmu_read(addr, ppu)

def jmp_iim8(cpu, mb, ppu): # 0x6C
    # 6502には重大なバグがあり、ページをまたいだ間接アドレス参照の場合、上位アドレスは
    # 当該ページの先頭アドレスの参照となる
    addr = mb.mmu_read(cpu.PC + 1, ppu) | mb.mmu_read(cpu.PC + 2, ppu) << 8
    addr_l = mb.mmu_read(addr % 0x10000, ppu)
    if addr & 0x00FF == 0xFF:
        addr_h = mb.mmu_read((addr & 0xFF00) % 0x10000, ppu)
    else:
        addr_h = mb.mmu_read((addr + 1) % 0x10000, ppu)
    cpu.PC = addr_l | addr_h << 8

# JSR命令
def jsr(cpu, mb, ppu): # 0x20
    # pushするアドレスは次命令の１個前
    rtn_addr_h = ((cpu.PC + 2) & 0xFF00) >> 8
    rtn_addr_l = (cpu.PC + 2) & 0x00FF
    mb.mmu_write(cpu.SP | 0x100, rtn_addr_h, ppu)
    cpu.SP -= 1
    mb.mmu_write(cpu.SP | 0x100, rtn_addr_l, ppu)
    cpu.SP -= 1
    #jmp_im16(cpu, mb) <- ダメっぽい
    cpu.PC = im16_ads(cpu, mb, ppu)

# RTS命令
def rts(cpu, mb, ppu): # 0x60
    cpu.SP += 1
    rtn_addr_l = mb.mmu_read(cpu.SP | 0x100, ppu)
    cpu.SP += 1
    rtn_addr_h = mb.mmu_read(cpu.SP| 0x100, ppu)
    cpu.PC = rtn_addr_l | rtn_addr_h << 8
    cpu.PC += 1 # <-これ重要

# RTI命令
def rti(cpu, mb, ppu): # 0x40
    plp(cpu, mb, ppu)
    cpu.SP += 1
    rtn_addr_l= mb.mmu_read(0x100 | cpu.SP, ppu)
    cpu.SP += 1
    rtn_addr_h = mb.mmu_read(0x100 | cpu.SP, ppu)
    cpu.PC = rtn_addr_l | rtn_addr_h << 8
    
# 分岐命令
# BCC命令
def bcc(cpu, mb, ppu): # 0x90
    if cpu.P['C'] == False:
        value = im8_ads(cpu, mb, ppu)
        cpu.PC += -(value & 0x80) | (value & 0x7F) + 2
    else:
        cpu.PC += 2

# BCS命令
def bcs(cpu, mb, ppu): # 0xB0
    if cpu.P['C'] == True:
        value = im8_ads(cpu, mb, ppu)
        cpu.PC += -(value & 0x80) | (value & 0x7F) + 2
    else:
        cpu.PC += 2

# BEQ命令
def beq(cpu, mb, ppu): # 0xF0
    if cpu.P['Z'] == True:
        value = im8_ads(cpu, mb, ppu)
        cpu.PC += -(value & 0x80) | (value & 0x7F) + 2
    else:
        cpu.PC += 2

# BMI命令
def bmi(cpu, mb, ppu): # 0x30
    if cpu.P['N'] == True:
        value = im8_ads(cpu, mb, ppu)
        cpu.PC += -(value & 0x80) | (value & 0x7F) + 2
    else:
        cpu.PC += 2

# BNE命令
def bne(cpu, mb, ppu): # 0xD0
    if cpu.P['Z'] == False:
        value = im8_ads(cpu, mb, ppu)
        cpu.PC += -(value & 0x80) | (value & 0x7F) + 2
    else:
        cpu.PC += 2
    
# BPL命令
def bpl(cpu, mb, ppu): # 0x10
    if cpu.P['N'] == False:
    #if (cpu.A & 0x80) == 0:
        value = im8_ads(cpu, mb, ppu)
        cpu.PC += -(value & 0x80) | (value & 0x7F) + 2
    else:
        cpu.PC += 2
    
# BVC命令
def bvc(cpu, mb, ppu): # 0x50
    if cpu.P['V'] == False:
        value = im8_ads(cpu, mb, ppu)
        cpu.PC += -(value & 0x80) | (value & 0x7F) + 2
    else:
        cpu.PC += 2
    
# BVS命令
def bvs(cpu, mb, ppu): # 0x70
    if cpu.P['V'] == True:
        value = im8_ads(cpu, mb, ppu)
        cpu.PC += -(value & 0x80) | (value & 0x7F) + 2
    else:
        cpu.PC += 2
    
# フラグ変更命令
# CLC命令
def clc(cpu, mb): # 0x18
    cpu.PC += 1
    cpu.P['C'] = False

# CLD命令　BCDモードからの復帰らしい
def cld(cpu, mb): # 0xD8
    cpu.PC += 1
    cpu.P['D'] = False

# CLI命令
def cli(cpu, mb): # 0x58
    cpu.PC += 1
    cpu.P['I'] = False

# CLV命令
def clv(cpu, mb): # 0xB8
    cpu.PC += 1
    cpu.P['V'] = False

# SEC命令
def sec(cpu, mb): # 0x38
    cpu.PC += 1
    cpu.P['C'] = True

# SED命令
def sed(cpu, mb): # 0xF8
    cpu.PC += 1
    cpu.P['D'] = True

# SEI命令
def sei(cpu, mb): # 0x78
    cpu.PC += 1
    cpu.P['I'] = True

# BRK(ソフトウェア割り込み)命令
def brk(cpu, mb, ppu): # 0x00
    if cpu.P["I"] == False:
        cpu.P["B"] = True
        cpu.PC += cpu.op_len[cpu.fetch(mb)]
        cpu.push(mb, (cpu.PC >> 8) & 0x00FF, ppu)
        cpu.push(mb, cpu.PC & 0x00FF, ppu)
        data = 0x00
        bitmask = 0x80
        for i in cpu.P.values():
            if i == True:
                data |= bitmask
            bitmask >>= 1
        cpu.push(mb, data, ppu)
        cpu.PC = mb.mmu_read(0xFFFE, ppu) | mb.mmu_read(0xFFFF, ppu) << 8

# NOP命令
def nop(cpu, mb): # 0xEA
    cpu.PC += 1

# 非公式命令
# NOP命令
def undef_nop1(cpu, mb): # 0x04 44 64
    cpu.PC += 2

def undef_nop2(cpu, mb): # 0x0C
    cpu.PC += 3
# LAX
def lax_iim8x(cpu, mb, ppu): # 0xA3
    addr = iim8x_ads(cpu, mb, ppu)
    cpu.A = mb.mmu_read(addr, ppu)
    set_f_zn(cpu, cpu.A)
    cpu.X = cpu.A
    set_f_zn(cpu, cpu.X)
    cpu.PC += 2

def lax_im8(cpu, mb, ppu): # 0xA7
    addr = im8_ads(cpu, mb, ppu)
    cpu.A = mb.mmu_read(addr, ppu)
    set_f_zn(cpu, cpu.A)
    cpu.X = cpu.A
    set_f_zn(cpu, cpu.X)
    cpu.PC += 2

def lax_im16(cpu, mb, ppu): # 0xAF
    addr = im16_ads(cpu, mb, ppu)
    cpu.A = mb.mmu_read(addr, ppu)
    set_f_zn(cpu, cpu.A)
    cpu.X = cpu.A
    set_f_zn(cpu, cpu.X)
    cpu.PC += 3

def lax_iim8y(cpu, mb, ppu): # 0xB3
    addr = iim8y_ads(cpu, mb, ppu)
    cpu.A = mb.mmu_read(addr, ppu)
    set_f_zn(cpu, cpu.A)
    cpu.X = cpu.A
    set_f_zn(cpu, cpu.X)
    cpu.PC += 2

def lax_im8y(cpu, mb, ppu): # 0xB7
    addr = im8y_ads(cpu, mb, ppu)
    cpu.A = mb.mmu_read(addr, ppu)
    set_f_zn(cpu, cpu.A)
    cpu.X = cpu.A
    set_f_zn(cpu, cpu.X)
    cpu.PC += 2

def lax_im16y(cpu, mb, ppu): # 0xBF
    addr = im16y_ads(cpu, mb, ppu)
    cpu.A = mb.mmu_read(addr, ppu)
    set_f_zn(cpu, cpu.A)
    cpu.X = cpu.A
    set_f_zn(cpu, cpu.X)
    cpu.PC += 3

# SAX命令
def sax_iim8x(cpu, mb, ppu): # 0x83
    addr = iim8x_ads(cpu, mb, ppu)
    mb.mmu_write(addr, cpu.A & cpu.X, ppu)
    cpu.PC += 2

def sax_im8(cpu, mb, ppu): # 0x87
    addr = im8_ads(cpu, mb, ppu)
    mb.mmu_write(addr, cpu.A & cpu.X, ppu)
    cpu.PC += 2

def sax_im16(cpu, mb, ppu): # 0x8F
    addr = im16_ads(cpu, mb, ppu)
    mb.mmu_write(addr, cpu.A & cpu.X, ppu)
    cpu.PC += 3

def sax_im8x(cpu, mb, ppu): # 0x97
    addr = im8x_ads(cpu, mb, ppu)
    mb.mmu_write(addr, cpu.A & cpu.X, ppu)
    cpu.PC += 2