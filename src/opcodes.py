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
    #cpu.PC += cpu.op_len[cpu.fetch(mb)]
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
    cpu.PC = mb.mmu_read(0xFFFA) | mb.mmu_read(0xFFFB) << 8

# アドレッシングモード
def sim8_ads(cpu, mb):
    return mb.mmu_read(cpu.PC + 1)

def im8_ads(cpu, mb):
    return mb.mmu_read(cpu.PC + 1) & 0x00FF

def im8x_ads(cpu, mb):
    return (mb.mmu_read(cpu.PC + 1) + cpu.X) & 0x00FF

def im8y_ads(cpu, mb):
    return (mb.mmu_read(cpu.PC + 1) + cpu.Y) & 0x00FF

def im16_ads(cpu, mb):
    return mb.mmu_read(cpu.PC + 1) | mb.mmu_read(cpu.PC + 2) << 8

def im16x_ads(cpu, mb):
    return (mb.mmu_read(cpu.PC + 1) | mb.mmu_read(cpu.PC + 2) << 8) + cpu.X

def im16y_ads(cpu, mb):
    return (mb.mmu_read(cpu.PC + 1) | mb.mmu_read(cpu.PC + 2) << 8) + cpu.Y

def iim8x_ads(cpu, mb):
    addr = (mb.mmu_read(cpu.PC + 1) | cpu.X) & 0x00FF
    addr_l = mb.mmu_read(addr)
    addr_h = mb.mmu_read(addr + 1)
    return addr_l | addr_h << 8

def iim8y_ads(cpu, mb):
    addr = mb.mmu_read(cpu.PC + 1) & 0x00FF
    addr_l = mb.mmu_read(addr)
    addr_h = mb.mmu_read(addr + 1)
    return (addr_l | addr_h << 8) + cpu.Y


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
def lda_sim8(cpu, mb): # 0xA9
    cpu.A = sim8_ads(cpu, mb)
    cpu.cycles += 2
    cpu.PC += 2
    set_f_zn(cpu, cpu.A)

def lda_im8(cpu, mb): # 0xA5
    addr = im8_ads(cpu, mb)
    cpu.A = mb.mmu_read(addr)
    cpu.cycles += 3
    cpu.PC += 2
    set_f_zn(cpu, cpu.A)

def lda_im8x(cpu, mb): # 0xB5
    addr = im8x_ads(cpu, mb)
    cpu.A = mb.mmu_read(addr)
    cpu.cycles += 4
    cpu.PC += 2
    set_f_zn(cpu, cpu.A)

def lda_im16(cpu, mb): # 0xAD
    addr = im16_ads(cpu, mb)
    cpu.A = mb.mmu_read(addr)
    cpu.cycles += 4
    cpu.PC += 3
    set_f_zn(cpu, cpu.A)

def lda_im16x(cpu, mb): # 0xBD
    addr = im16x_ads(cpu, mb)
    cpu.A = mb.mmu_read(addr)
    cpu.cycles += 4
    cpu.PC += 3
    set_f_zn(cpu, cpu.A)

def lda_im16y(cpu, mb): # 0xB9
    addr = im16y_ads(cpu, mb)
    cpu.A = mb.mmu_read(addr)
    cpu.cycles += 4
    cpu.PC += 3
    set_f_zn(cpu, cpu.A)

def lda_iim8x(cpu, mb): # 0xA1
    addr = iim8x_ads(cpu, mb)
    cpu.A = mb.mmu_read(addr)
    cpu.cycles += 6
    cpu.PC += 2
    set_f_zn(cpu, cpu.A)

def lda_iim8y(cpu, mb): # 0xB1
    addr = iim8y_ads(cpu, mb)
    cpu.A = mb.mmu_read(addr)
    cpu.cycles += 5
    cpu.PC += 2
    set_f_zn(cpu, cpu.A)

# LDX命令
def ldx_sim8(cpu, mb): # 0xA2
    cpu.X = sim8_ads(cpu, mb)
    cpu.cycles += 2
    cpu.PC += 2
    set_f_zn(cpu, cpu.X)

def ldx_im8(cpu, mb): # 0xA6
    addr = im8_ads(cpu, mb)
    cpu.X = mb.mmu_read(addr)
    cpu.cycles += 3
    cpu.PC += 2
    set_f_zn(cpu, cpu.X)

def ldx_im8y(cpu, mb): # 0xB6
    addr = im8y_ads(cpu, mb)
    cpu.X = mb.mmu_read(addr)
    cpu.cycles += 4
    cpu.PC += 2
    set_f_zn(cpu, cpu.X)

def ldx_im16(cpu, mb): # 0xAE
    addr = im16_ads(cpu, mb)
    cpu.X = mb.mmu_read(addr)
    cpu.cycles += 4
    cpu.PC += 3
    set_f_zn(cpu, cpu.X)

def ldx_im16y(cpu, mb): # 0xBE
    addr = im16y_ads(cpu, mb)
    cpu.X = mb.mmu_read(addr)
    cpu.cycles += 4
    cpu.PC += 3
    set_f_zn(cpu, cpu.X)

# LDY命令
def ldy_sim8(cpu, mb): # 0xA0
    cpu.Y = sim8_ads(cpu, mb)
    cpu.cycles += 2
    cpu.PC += 2
    set_f_zn(cpu, cpu.Y)

def ldy_im8(cpu, mb): # 0xA4
    addr = im8_ads(cpu, mb)
    cpu.Y = mb.mmu_read(addr)
    cpu.cycles += 3
    cpu.PC += 2
    set_f_zn(cpu, cpu.Y)

def ldy_im8x(cpu, mb): # 0xB4
    addr = im8x_ads(cpu, mb)
    cpu.Y = mb.mmu_read(addr)
    cpu.cycles += 4
    cpu.PC += 2
    set_f_zn(cpu, cpu.Y)

def ldy_im16(cpu, mb): # 0xAC
    addr = im16_ads(cpu, mb)
    cpu.Y = mb.mmu_read(addr)
    cpu.cycles += 4
    cpu.PC += 3
    set_f_zn(cpu, cpu.Y)

def ldy_im16x(cpu, mb): # 0xBC
    addr = im16x_ads(cpu, mb)
    cpu.Y = mb.mmu_read(addr)
    cpu.cycles += 4
    cpu.PC += 3
    set_f_zn(cpu, cpu.Y)

# STA命令
def sta_im8(cpu, mb, ppu): # 0x85
    addr = im8_ads(cpu, mb)
    mb.mmu_write(addr, cpu.A, ppu)
    cpu.cycles += 3
    cpu.PC += 2

def sta_im8x(cpu, mb, ppu): # 0x95
    addr = im8x_ads(cpu, mb)
    mb.mmu_write(addr, cpu.A, ppu)
    cpu.cycles += 4
    cpu.PC += 2

def sta_im16(cpu, mb, ppu): # 0x8D
    addr = im16_ads(cpu, mb)
    mb.mmu_write(addr, cpu.A, ppu)
    cpu.cycles += 4
    cpu.PC += 3

def sta_im16x(cpu, mb, ppu): # 0x9D
    addr = im16x_ads(cpu, mb)
    mb.mmu_write(addr, cpu.A, ppu)
    cpu.cycles += 5
    cpu.PC += 3

def sta_im16y(cpu, mb, ppu): # 0x99
    addr = im16y_ads(cpu, mb)
    mb.mmu_write(addr, cpu.A, ppu)
    cpu.cycles += 5
    cpu.PC += 3

def sta_iim8x(cpu, mb, ppu): # 0x81
    addr = iim8x_ads(cpu, mb)
    mb.mmu_write(addr, cpu.A, ppu)
    cpu.cycles += 6
    cpu.PC += 2

def sta_iim8y(cpu, mb, ppu): # 0x91
    addr = iim8y_ads(cpu, mb)
    mb.mmu_write(addr)
    cpu.cycles += 6
    cpu.PC += 2

# STX命令
def stx_im8(cpu, mb, ppu): # 0x86
    addr = im8_ads(cpu, mb)
    mb.mmu_write(addr, cpu.X, ppu)
    cpu.cycles += 3
    cpu.PC += 2

def stx_im8y(cpu, mb, ppu): # 0x96
    addr = im8y_ads(cpu, mb)
    mb.mmu_write(addr, cpu.X, ppu)
    cpu.cycles += 4
    cpu.PC += 2

def stx_im16(cpu, mb, ppu): # 0x8E
    addr = im16_ads(cpu, mb)
    mb.mmu_write(addr, cpu.X, ppu)
    cpu.cycles += 4
    cpu.PC += 3

# STY命令
def sty_im8(cpu, mb, ppu): # 0x84
    addr = im8_ads(cpu, mb)
    mb.mmu_write(addr, cpu.Y, ppu)
    cpu.cycles += 3
    cpu.PC += 2

def sty_im8x(cpu, mb, ppu): # 0x94
    addr = im8x_ads(cpu, mb)
    mb.mmu_write(addr, cpu.Y, ppu)
    cpu.cycles += 4
    cpu.PC += 2

def sty_im16(cpu, mb, ppu): # 0x8C
    addr = im16_ads(cpu, mb)
    mb.mmu_write(addr, cpu.Y, ppu)
    cpu.cycles += 4
    cpu.PC += 3

# TAX命令
def tax(cpu, mb): # 0xAA
    cpu.X = cpu.A
    cpu.cycles += 2
    cpu.PC += 1
    set_f_zn(cpu, cpu.X)

# TAY命令
def tay(cpu, mb): # 0xA8
    cpu.Y = cpu.A
    cpu.cycles += 2
    cpu.PC += 1
    set_f_zn(cpu, cpu.Y)

# TSX命令
def tsx(cpu, mb): # 0xBA
    cpu.X = cpu.SP & 0x00FF
    cpu.cycles += 2
    cpu.PC += 1
    set_f_zn(cpu, cpu.X)

# TXA命令
def txa(cpu, mb): # 0x8A
    cpu.A = cpu.X
    cpu.cycles += 2
    cpu.PC += 1
    set_f_zn(cpu, cpu.A)

# TXS命令
def txs(cpu, mb): # 0x9A
    cpu.SP = cpu.X | 0x0100
    cpu.cycles += 2
    cpu.PC += 1
    set_f_zn(cpu, cpu.SP)

# TYA命令
def tya(cpu, mb): # 0x98
    cpu.A = cpu.Y
    cpu.cycles += 2
    cpu.PC += 1
    set_f_zn(cpu, cpu.A)

# 算術命令
# ADC命令
def adc_sim8(cpu, mb): # 0x69
    data = sim8_ads(cpu, mb)
    value = cpu.A + data + int(cpu.P['C'])
    cpu.P['C'] = (value & 0x100) > 0
    cpu.P['V'] = (((cpu.A ^ value) & (data ^ value)) & 0x80) > 0
    cpu.A = value & 0x00FF
    set_f_zn(cpu, cpu.A)
    cpu.cycles += 2
    cpu.PC += 2

def adc_im8(cpu, mb): # 0x65
    addr = im8_ads(cpu, mb)
    value = (cpu.A + mb.mmu_read(addr) + int(cpu.P['C'])) % 0x100
    cpu.P['V'] = (((cpu.A ^ value) & (mb.mmu_read(addr) ^ value)) & 0x80) > 0
    cpu.P['C'] = (value & 0x100) > 0
    cpu.A = value
    set_f_zn(cpu, cpu.A)
    cpu.cycles += 3
    cpu.PC += 2

def adc_im8x(cpu, mb): # 0x75
    addr = im8x_ads(cpu, mb)
    value = (cpu.A + mb.mmu_read(addr) + int(cpu.P['C'])) % 0x100
    cpu.P['V'] = (((cpu.A ^ value) & (mb.mmu_read(addr) ^ value)) & 0x80) > 0
    cpu.P['C'] = (value & 0x100) > 0
    cpu.A = value
    set_f_zn(cpu, cpu.A)
    cpu.cycles += 4
    cpu.PC += 2

def adc_im16(cpu, mb): # 0x6D
    addr = im16_ads(cpu, mb)
    value = (cpu.A + mb.mmu_read(addr) + int(cpu.P['C'])) % 0x100
    cpu.P['V'] = (((cpu.A ^ value) & (mb.mmu_read(addr) ^ value)) & 0x80) > 0
    cpu.P['C'] = (value & 0x100) > 0
    cpu.A = value
    set_f_zn(cpu, cpu.A)
    cpu.cycles += 4
    cpu.PC += 3

def adc_im16x(cpu, mb): # 0x7D
    addr = im16x_ads(cpu, mb)
    value = (cpu.A + mb.mmu_read(addr) + int(cpu.P['C'])) % 0x100
    cpu.P['V'] = (((cpu.A ^ value) & (mb.mmu_read(addr) ^ value)) & 0x80) > 0
    cpu.P['C'] = (value & 0x100) > 0
    cpu.A = value
    set_f_zn(cpu, cpu.A)
    cpu.cycles += 4
    cpu.PC += 3

def adc_im16y(cpu, mb): # 0x79
    addr = im16y_ads(cpu, mb)
    value = (cpu.A + mb.mmu_read(addr) + int(cpu.P['C'])) % 0x100
    cpu.P['V'] = (((cpu.A ^ value) & (mb.mmu_read(addr) ^ value)) & 0x80) > 0
    cpu.P['C'] = (value & 0x100) > 0
    cpu.A = value
    set_f_zn(cpu, cpu.A)
    cpu.cycles += 4
    cpu.PC += 3

def adc_iim8x(cpu, mb): # 0x61
    addr = im16y_ads(cpu, mb)
    value = (cpu.A + mb.mmu_read(addr) + int(cpu.P['C'])) % 0x100
    cpu.P['V'] = (((cpu.A ^ value) & (mb.mmu_read(addr) ^ value)) & 0x80) > 0
    cpu.P['C'] = (value & 0x100) > 0
    cpu.A = value
    set_f_zn(cpu, cpu.A)
    cpu.cycles += 6
    cpu.PC += 2

def adc_iim8y(cpu, mb): # 0x71
    addr = im16y_ads(cpu, mb)
    value = (cpu.A + mb.mmu_read(addr) + int(cpu.P['C'])) % 0x100
    cpu.P['V'] = (((cpu.A ^ value) & (mb.mmu_read(addr) ^ value)) & 0x80) > 0
    cpu.P['C'] = (value & 0x100) > 0
    cpu.A = value
    set_f_zn(cpu, cpu.A)
    cpu.cycles += 5
    cpu.PC += 2

# ADC命令
def and_sim8(cpu, mb): # 0x29
    cpu.A &= sim8_ads(cpu, mb)
    set_f_zn(cpu, cpu.A)
    cpu.cycles += 2
    cpu.PC += 2

def and_im8(cpu, mb): # 0x25
    addr = im8_ads(cpu, mb)
    cpu.A &= mb.mmu_read(addr)
    set_f_zn(cpu, cpu.A)
    cpu.cycles += 3
    cpu.PC += 2

def and_im8x(cpu, mb): # 0x35
    addr = im8x_ads(cpu, mb)
    cpu.A &= mb.mmu_read(addr)
    set_f_zn(cpu, cpu.A)
    cpu.cycles += 4
    cpu.PC += 2

def and_im16(cpu, mb): # 0x2D
    addr = im16_ads(cpu, mb)
    cpu.A &= mb.mmu_read(addr)
    set_f_zn(cpu, cpu.A)
    cpu.cycles += 4
    cpu.PC += 3

def and_im16x(cpu, mb): # 0x3D
    addr = im16x_ads(cpu, mb)
    cpu.A &= mb.mmu_read(addr)
    set_f_zn(cpu, cpu.A)
    cpu.cycles += 4
    cpu.PC += 3

def and_im16y(cpu, mb): # 0x39
    addr = im16y_ads(cpu, mb)
    cpu.A &= mb.mmu_read(addr)
    set_f_zn(cpu, cpu.A)
    cpu.cycles += 4
    cpu.PC += 3

def and_iim8x(cpu, mb): # 0x21
    addr = iim8x_ads(cpu, mb)
    cpu.A &= mb.mmu_read(addr)
    set_f_zn(cpu, cpu.A)
    cpu.cycles += 6
    cpu.PC += 2

def and_iim8y(cpu, mb): # 0x31
    addr = iim8y_ads(cpu, mb)
    cpu.A &= mb.mmu_read(addr)
    set_f_zn(cpu, cpu.A)
    cpu.cycles += 5
    cpu.PC += 2

# ASL命令
def asl_acc(cpu, mb): # 0x0A
    cpu.P['C'] = (cpu.A & 0x80) > 0
    cpu.A <<= 1
    cpu.A &= 0x00FF
    set_f_zn(cpu, cpu.A)
    cpu.cycles += 2
    cpu.PC += 1

def asl_im8(cpu, mb): # 0x06
    addr = im8_ads(cpu, mb)
    value = mb.mmu_read(addr)
    cpu.P['C'] = (value & 0x80) > 0
    value <<= 1
    value = value & 0x00FF
    mb.mmu_write(addr, value, ppu)
    set_f_zn(cpu, value)
    cpu.cycles += 5
    cpu.PC += 2

def asl_im8x(cpu, mb): # 0x16
    addr = im8x_ads(cpu, mb)
    value = mb.mmu_read(addr)
    cpu.P['C'] = (value & 0x80) > 0
    value <<= 1
    value = value & 0x00FF
    mb.mmu_write(addr, value, ppu)
    set_f_zn(cpu, value)
    cpu.cycles += 6
    cpu.PC += 2

def asl_im16(cpu, mb): # 0x0E
    addr = im16_ads(cpu, mb)
    value = mb.mmu_read(addr)
    cpu.P['C'] = (value & 0x80) > 0
    value <<= 1
    value = value & 0x00FF
    mb.mmu_write(addr, value, ppu)
    set_f_zn(cpu, value)
    cpu.cycles += 6
    cpu.PC += 2

def asl_im16x(cpu, mb): # 0x1E
    addr = im16x_ads(cpu, mb)
    value = mb.mmu_read(addr)
    cpu.P['C'] = (value & 0x80) > 0
    value <<= 1
    value = value & 0x00FF
    mb.mmu_write(addr, value, ppu)
    set_f_zn(cpu, value)
    cpu.cycles += 7
    cpu.PC += 2

# BIT命令
def bit_im8(cpu, mb): # 0x24
    addr = im8_ads(cpu, mb)
    value = mb.mmu_read(addr)
    cpu.P['N'] = (value & 0x80) > 0
    cpu.P['V'] = (value & 0x40) > 0
    cpu.P['Z'] = (value & cpu.A) == 0
    cpu.cycles += 3
    cpu.PC += 2

def bit_im16(cpu, mb): # 0x2C
    addr = im16_ads(cpu, mb)
    value = mb.mmu_read(addr)
    cpu.P['N'] = (value & 0x80) > 0
    cpu.P['V'] = (value & 0x40) > 0
    cpu.P['Z'] = (value & cpu.A) == 0
    cpu.cycles += 4
    cpu.PC += 3

# CMP命令
def cmp_sim8(cpu, mb): # 0xC9
    data = sim8_ads(cpu, mb)
    diff = dec_uint8(cpu.A, data)
    set_f_zn(cpu, diff)
    cpu.P['C'] = not (cpu.A < data) 
    cpu.cycles += 2
    cpu.PC += 2

def cmp_im8(cpu, mb): # 0xC5
    addr = im8_ads(cpu, mb)
    data = mb.mmu_read(addr)
    diff = dec_uint8(cpu.A, data)
    set_f_zn(cpu, diff)
    cpu.P['C'] = not (cpu.A < data) 
    cpu.cycles += 3
    cpu.PC += 2

def cmp_im8x(cpu, mb): # 0xD5
    addr = im8x_ads(cpu, mb)
    data = mb.mmu_read(addr)
    diff = dec_uint8(cpu.A, data)
    set_f_zn(cpu, diff)
    cpu.P['C'] = not (cpu.A < data) 
    cpu.cycles += 4
    cpu.PC += 2

def cmp_im16(cpu, mb): # 0xCD
    addr = im16_ads(cpu, mb)
    data = mb.mmu_read(addr)
    diff = dec_uint8(cpu.A, data)
    set_f_zn(cpu, diff)
    cpu.P['C'] = not (cpu.A < data) 
    cpu.cycles += 4
    cpu.PC += 3

def cmp_im16x(cpu, mb): # 0xDD
    addr = im16x_ads(cpu, mb)
    data = mb.mmu_read(addr)
    diff = dec_uint8(cpu.A, data)
    set_f_zn(cpu, diff)
    cpu.P['C'] = not (cpu.A < data) 
    cpu.cycles += 4
    cpu.PC += 3

def cmp_im16y(cpu, mb): # 0xD9
    addr = im16y_ads(cpu, mb)
    data = mb.mmu_read(addr)
    diff = dec_uint8(cpu.A, data)
    set_f_zn(cpu, diff)
    cpu.P['C'] = not (cpu.A < data) 
    cpu.cycles += 4
    cpu.PC += 3

def cmp_iim8x(cpu, mb): # 0xC1
    addr = iim8y_ads(cpu, mb)
    data = mb.mmu_read(addr)
    diff = dec_uint8(cpu.A, data)
    set_f_zn(cpu, diff)
    cpu.P['C'] = not (cpu.A < data) 
    cpu.cycles += 6
    cpu.PC += 2

def cmp_iim8y(cpu, mb): # 0xD1
    addr = iim8y_ads(cpu, mb)
    data = mb.mmu_read(addr)
    diff = dec_uint8(cpu.A, data)
    set_f_zn(cpu, diff)
    cpu.P['C'] = not (cpu.A < data) 
    cpu.cycles += 5
    cpu.PC += 2

# CPX命令
def cpx_sim8(cpu, mb): # 0xE0
    data = sim8_ads(cpu, mb)
    diff = dec_uint8(cpu.X, data)
    set_f_zn(cpu, diff)
    cpu.P['C'] = not (cpu.X < data)
    cpu.cycles += 2
    cpu.PC += 2

def cpx_im8(cpu, mb): # 0xE4
    addr = im8_ads(cpu, mb)
    data = mb.mmu_read(addr)
    diff = dec_uint8(cpu.X, data)
    set_f_zn(cpu, diff)
    cpu.P['C'] = not (cpu.X < data)
    cpu.cycles += 3
    cpu.PC += 2

def cpx_im16(cpu, mb): # 0xEC
    addr = im16_ads(cpu, mb)
    data = mb.mmu_read(addr)
    diff = dec_uint8(cpu.X, data)
    set_f_zn(cpu, diff)
    cpu.P['C'] = not (cpu.X < data)
    cpu.cycles += 4
    cpu.PC += 3

# CPY命令
def cpy_sim8(cpu, mb): # 0xC0
    data = sim8_ads(cpu, mb)
    diff = dec_uint8(cpu.Y, data)
    set_f_zn(cpu, diff)
    cpu.P['C'] = not (cpu.Y < data)
    cpu.cycles += 2
    cpu.PC += 2

def cpy_im8(cpu, mb): # 0xC4
    addr = im8_ads(cpu, mb)
    data = mb.mmu_read(addr)
    diff = dec_uint8(cpu.Y, data)
    set_f_zn(cpu, diff)
    cpu.P['C'] = not (cpu.Y < data)
    cpu.cycles += 2
    cpu.PC += 2

def cpy_im16(cpu, mb): # 0xCC
    addr = im16_ads(cpu, mb)
    data = mb.mmu_read(addr)
    diff = dec_uint8(cpu.Y, data)
    set_f_zn(cpu, diff)
    cpu.P['C'] = not (cpu.Y < data)
    cpu.cycles += 4
    cpu.PC += 3

# DEC命令
def dec_im8(cpu, mb): # 0xC6
    addr = im8_ads(cpu, mb)
    value = dec_uint8(mb.mmu_read(addr), 1)
    mb.mmu_write(addr, value, ppu)
    set_f_zn(cpu, value)
    cpu.cycles += 5
    cpu.PC += 2

def dec_im8x(cpu, mb): # 0xD6
    addr = im8x_ads(cpu, mb)
    value = dec_uint8(mb.mmu_read(addr), 1)
    mb.mmu_write(addr, value, ppu)
    set_f_zn(cpu, value)
    cpu.cycles += 6
    cpu.PC += 2

def dec_im16(cpu, mb): # 0xCE
    addr = im16_ads(cpu, mb)
    value = dec_uint8(mb.mmu_read(addr), 1)
    mb.mmu_write(addr, value, ppu)
    set_f_zn(cpu, value)
    cpu.cycles += 6
    cpu.PC += 3

def dec_im16x(cpu, mb): # 0xDE
    addr = im16x_ads(cpu, mb)
    value = dec_uint8(mb.mmu_read(addr), 1)
    mb.mmu_write(addr, value, ppu)
    set_f_zn(cpu, value)
    cpu.cycles += 7
    cpu.PC += 3

# DEX命令
def dex(cpu, mb): # 0xCA
    cpu.X = dec_uint8(cpu.X, 1)
    cpu.cycles += 2
    cpu.PC += 1
    set_f_zn(cpu, cpu.X)

# DEY命令
def dey(cpu, mb): # 0x88
    cpu.Y = dec_uint8(cpu.Y, 1)
    cpu.cycles += 2
    cpu.PC += 1
    set_f_zn(cpu, cpu.Y)

# EOR命令
def eor_sim8(cpu, mb): # 0x49
    cpu.A ^= sim8_ads(cpu, mb)
    set_f_zn(cpu, cpu.A)
    cpu.cycles += 2
    cpu.PC += 2

def eor_im8(cpu, mb): # 0x45
    addr = im8_ads(cpu, mb)
    cpu.A ^= mb.mmu_read(addr)
    set_f_zn(cpu, cpu.A)
    cpu.cycles += 3
    cpu.PC += 2

def eor_im8(cpu, mb): # 0x55
    addr = im8x_ads(cpu, mb)
    cpu.A ^= mb.mmu_read(addr)
    set_f_zn(cpu, cpu.A)
    cpu.cycles += 4
    cpu.PC += 2

def eor_im16(cpu, mb): # 0x4D
    addr = im16_ads(cpu, mb)
    cpu.A ^= mb.mmu_read(addr)
    set_f_zn(cpu, cpu.A)
    cpu.cycles += 4
    cpu.PC += 3

def eor_im16x(cpu, mb): # 0x4D
    addr = im16x_ads(cpu, mb)
    cpu.A ^= mb.mmu_read(addr)
    set_f_zn(cpu, cpu.A)
    cpu.cycles += 4
    cpu.PC += 3

def eor_im16y(cpu, mb): # 0x4D
    addr = im16y_ads(cpu, mb)
    cpu.A ^= mb.mmu_read(addr)
    set_f_zn(cpu, cpu.A)
    cpu.cycles += 4
    cpu.PC += 3

def eor_iim16x(cpu, mb): # 0x41
    addr = iim16x_ads(cpu, mb)
    cpu.A ^= mb.mmu_read(addr)
    set_f_zn(cpu, cpu.A)
    cpu.cycles += 6
    cpu.PC += 2

def eor_iim16y(cpu, mb): # 0x51
    addr = iim16y_ads(cpu, mb)
    cpu.A ^= mb.mmu_read(addr)
    set_f_zn(cpu, cpu.A)
    cpu.cycles += 5
    cpu.PC += 2

# INC命令
def inc_im8(cpu, mb, ppu): # 0xE6
    addr = im8_ads(cpu, mb)
    value = (mb.mmu_read(addr) + 1) & 0x00FF
    mb.mmu_write(addr, value, ppu)
    set_f_zn(cpu, value)
    cpu.cycles += 5
    cpu.PC += 2

def inc_im8x(cpu, mb, ppu): # 0xF6
    addr = im8x_ads(cpu, mb)
    value = (mb.mmu_read(addr) + 1) & 0x00FF
    mb.mmu_write(addr, value, ppu)
    set_f_zn(cpu, value)
    cpu.cycles += 6
    cpu.PC += 2

def inc_im16(cpu, mb, ppu): # 0xEE
    addr = im16_ads(cpu, mb)
    value = (mb.mmu_read(addr) + 1) & 0x00FF
    mb.mmu_write(addr, value, ppu)
    set_f_zn(cpu, value)
    cpu.cycles += 6
    cpu.PC += 3

def inc_im16x(cpu, mb, ppu): # 0xFE
    addr = im16x_ads(cpu, mb)
    value = (mb.mmu_read(addr) + 1) & 0x00FF
    mb.mmu_write(addr, value, ppu)
    set_f_zn(cpu, value)
    cpu.cycles += 7
    cpu.PC += 3

# INX命令
def inx(cpu, mb): # 0xE8
    cpu.X = (cpu.X + 1) & 0x00FF
    cpu.cycles += 2
    cpu.PC += 1
    set_f_zn(cpu, cpu.X)

# INY命令
def iny(cpu, mb): # 0xC8
    cpu.Y = (cpu.Y + 1) & 0x00FF
    cpu.cycles += 2
    cpu.PC += 1
    set_f_zn(cpu, cpu.Y)

# LSR命令
def lsr_acc(cpu, mb): # 0x4A
    cpu.P['C'] = (cpu.A & 0x01) > 0
    cpu.A >>= 1
    set_f_zn(cpu, cpu.A)
    cpu.cycles += 2
    cpu.PC += 1

def lsr_im8(cpu, mb): # 0x46
    addr = im8_ads(cpu, mb)
    value = mb.mmu_read(addr)
    cpu.P['C'] = (value & 0x01) > 0
    value >>= 1
    mb.mmu_write(addr, value, ppu)
    set_f_zn(cpu, value)
    cpu.cycles += 5
    cpu.PC += 2

def lsr_im8x(cpu, mb): # 0x56
    addr = im8x_ads(cpu, mb)
    value = mb.mmu_read(addr)
    cpu.P['C'] = (value & 0x01) > 0
    value >>= 1
    mb.mmu_write(addr, value, ppu)
    set_f_zn(cpu, value)
    cpu.cycles += 6
    cpu.PC += 2

def lsr_im16(cpu, mb): # 0x4E
    addr = im16_ads(cpu, mb)
    value = mb.mmu_read(addr)
    cpu.P['C'] = (value & 0x01) > 0
    value >>= 1
    mb.mmu_write(addr, value, ppu)
    set_f_zn(cpu, value)
    cpu.cycles += 6
    cpu.PC += 3

def lsr_im16x(cpu, mb): # 0x5E
    addr = im16x_ads(cpu, mb)
    value = mb.mmu_read(addr)
    cpu.P['C'] = (value & 0x01) > 0
    value >>= 1
    mb.mmu_write(addr, value, ppu)
    set_f_zn(cpu, value)
    cpu.cycles += 7
    cpu.PC += 3
# ORA命令
def ora_sim8(cpu, mb): # 0x09
    cpu.A |= sim8_ads(cpu, mb)
    set_f_zn(cpu, cpu.A)
    cpu.cycles += 2
    cpu.PC += 2

def ora_im8(cpu, mb): # 0x05
    addr = im8_ads(cpu, mb)
    cpu.A |= mb.mmu_read(addr)
    set_f_zn(cpu, cpu.A)
    cpu.cycles += 3
    cpu.PC += 2

def ora_im8(cpu, mb): # 0x15
    addr = im8x_ads(cpu, mb)
    cpu.A |= mb.mmu_read(addr)
    set_f_zn(cpu, cpu.A)
    cpu.cycles += 4
    cpu.PC += 2

def ora_im16(cpu, mb): # 0x0D
    addr = im16_ads(cpu, mb)
    cpu.A |= mb.mmu_read(addr)
    set_f_zn(cpu, cpu.A)
    cpu.cycles += 4
    cpu.PC += 3

def ora_im16x(cpu, mb): # 0x1D
    addr = im16x_ads(cpu, mb)
    cpu.A |= mb.mmu_read(addr)
    set_f_zn(cpu, cpu.A)
    cpu.cycles += 4
    cpu.PC += 3

def ora_im16y(cpu, mb): # 0x19
    addr = im16y_ads(cpu, mb)
    cpu.A |= mb.mmu_read(addr)
    set_f_zn(cpu, cpu.A)
    cpu.cycles += 4
    cpu.PC += 3

def ora_iim16x(cpu, mb): # 0x01
    addr = iim8x_ads(cpu, mb)
    cpu.A |= mb.mmu_read(addr)
    set_f_zn(cpu, cpu.A)
    cpu.cycles += 6
    cpu.PC += 2

def ora_iim16y(cpu, mb): # 0x11
    addr = iim8y_ads(cpu, mb)
    cpu.A |= mb.mmu_read(addr)
    set_f_zn(cpu, cpu.A)
    cpu.cycles += 5
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
    cpu.cycles += 2
    cpu.PC += 1

def rol_im8(cpu, mb, ppu): # 0x26
    addr = im8_ads(cpu, mb)
    value = mb.mmu_read(addr)
    ogn_c = cpu.P['C'] > 0
    cpu.P['C'] = (value & 0x80) > 0
    value <<= 1
    value = value & 0x00FF
    if ogn_c:
        value |= 0x01
    mb.mmu_write(addr, value, ppu)
    set_f_zn(cpu, value)
    cpu.cycles += 5
    cpu.PC += 2

def rol_im8x(cpu, mb, ppu): # 0x36
    addr = im8x_ads(cpu, mb)
    value = mb.mmu_read(addr)
    ogn_c = cpu.P['C'] > 0
    cpu.P['C'] = (value & 0x80) > 0
    value <<= 1
    value = value & 0x00FF
    if ogn_c:
        value |= 0x01
    mb.mmu_write(addr, value, ppu)
    set_f_zn(cpu, value)
    cpu.cycles += 6
    cpu.PC += 2

def rol_im16(cpu, mb, ppu): # 0x2E
    addr = im16_ads(cpu, mb)
    value = mb.mmu_read(addr)
    ogn_c = cpu.P['C'] > 0
    cpu.P['C'] = (value & 0x80) > 0
    value <<= 1
    value = value & 0x00FF
    if ogn_c:
        value |= 0x01
    mb.mmu_write(addr, value, ppu)
    set_f_zn(cpu, value)
    cpu.cycles += 6
    cpu.PC += 3

def rol_im16x(cpu, mb, ppu): # 0x3E
    addr = im16x_ads(cpu, mb)
    value = mb.mmu_read(addr)
    ogn_c = cpu.P['C'] > 0
    cpu.P['C'] = (value & 0x80) > 0
    value <<= 1
    value = value & 0x00FF
    if ogn_c:
        value |= 0x01
    mb.mmu_write(addr, value, ppu)
    set_f_zn(cpu, value)
    cpu.cycles += 7
    cpu.PC += 3

# SBC命令 # 多分cフラグが間違い
def sbc_sim8(cpu, mb): # 0xE9
    data = sim8_ads(cpu, mb)
    value = dec_uint8_tri(cpu.A, data, int(not cpu.P['C']))
    cpu.P['V'] = (((cpu.A ^ value) & (data ^ value)) & 0x80) > 0
    cpu.P['C'] = not ((value & 0x100) > 0)
    cpu.A = value
    set_f_zn(cpu, cpu.A)
    cpu.cycles += 2
    cpu.PC += 2

def sbc_im8(cpu, mb): # 0xE5
    addr = im8_ads(cpu, mb)
    value = dec_uint8_tri(cpu.A, mb.mmu_read(addr), int(not cpu.P['C']))
    cpu.P['V'] = (((cpu.A ^ value) & (mb.mmu_read(addr) ^ value)) & 0x80) > 0
    cpu.P['C'] = not ((value & 0x100) > 0)
    cpu.A = value
    set_f_zn(cpu, cpu.A)
    cpu.cycles += 3
    cpu.PC += 2

def sbc_im8x(cpu, mb): # 0xF5
    addr = im8x_ads(cpu, mb)
    value = dec_uint8_tri(cpu.A, mb.mmu_read(addr), int(not cpu.P['C']))
    cpu.P['V'] = (((cpu.A ^ value) & (mb.mmu_read(addr) ^ value)) & 0x80) > 0
    cpu.P['C'] = not ((value & 0x100) > 0)
    cpu.A = value
    set_f_zn(cpu, cpu.A)
    cpu.cycles += 4
    cpu.PC += 2

def sbc_im16(cpu, mb): # 0xED
    addr = im16_ads(cpu, mb)
    value = dec_uint8_tri(cpu.A, mb.mmu_read(addr), int(not cpu.P['C']))
    cpu.P['V'] = (((cpu.A ^ value) & (mb.mmu_read(addr) ^ value)) & 0x80) > 0
    cpu.P['C'] = not ((value & 0x100) > 0)
    cpu.A = value
    set_f_zn(cpu, cpu.A)
    cpu.cycles += 4
    cpu.PC += 3

def sbc_im16x(cpu, mb): # 0xFD
    addr = im16x_ads(cpu, mb)
    value = dec_uint8_tri(cpu.A, mb.mmu_read(addr), int(not cpu.P['C']))
    cpu.P['V'] = (((cpu.A ^ value) & (mb.mmu_read(addr) ^ value)) & 0x80) > 0
    cpu.P['C'] = not ((value & 0x100) > 0)
    cpu.A = value
    set_f_zn(cpu, cpu.A)
    cpu.cycles += 4
    cpu.PC += 3

def sbc_im16y(cpu, mb): # 0xF9
    addr = im16y_ads(cpu, mb)
    value = dec_uint8_tri(cpu.A, mb.mmu_read(addr), int(not cpu.P['C']))
    cpu.P['V'] = (((cpu.A ^ value) & (mb.mmu_read(addr) ^ value)) & 0x80) > 0
    cpu.P['C'] = not ((value & 0x100) > 0)
    cpu.A = value
    set_f_zn(cpu, cpu.A)
    cpu.cycles += 4
    cpu.PC += 3

def sbc_iim8x(cpu, mb): # 0xE1
    addr = im16y_ads(cpu, mb)
    value = dec_uint8_tri(cpu.A, mb.mmu_read(addr), int(not cpu.P['C']))
    cpu.P['V'] = (((cpu.A ^ value) & (mb.mmu_read(addr) ^ value)) & 0x80) > 0
    cpu.P['C'] = not ((value & 0x100) > 0)
    cpu.A = value
    set_f_zn(cpu, cpu.A)
    cpu.cycles += 6
    cpu.PC += 2

def sbc_iim8y(cpu, mb): # 0xF1
    addr = im16y_ads(cpu, mb)
    value = dec_uint8_tri(cpu.A, mb.mmu_read(addr), int(not cpu.P['C']))
    cpu.P['V'] = (((cpu.A ^ value) & (mb.mmu_read(addr) ^ value)) & 0x80) > 0
    cpu.P['C'] = not ((value & 0x100) > 0)
    cpu.A = value
    set_f_zn(cpu, cpu.A)
    cpu.cycles += 5
    cpu.PC += 2

# スタック命令
# PHA命令
def pha(cpu, mb, ppu): # 0x48
    cpu.push(mb, cpu.A, ppu)
    cpu.cycles += 3
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
    cpu.cycles += 3
    cpu.PC += 1

# PLA命令
def pla(cpu, mb): # 0x68
    cpu.SP += 1
    cpu.A = mb.mmu_read(0x100 | cpu.SP)
    set_f_zn(cpu, cpu.A)
    cpu.cycles += 4
    cpu.PC += 1

# PLP命令
def plp(cpu, mb): # 0x28
    cpu.SP += 1
    value = mb.mmu_read(0x100 | cpu.SP)
    cpu.P["N"] = (value & 0x80) > 0
    cpu.P["V"] = (value & 0x40) > 0
    cpu.P["1"] = True # (value & 0x20) > 0
    cpu.P["B"] = (value & 0x10) > 0
    cpu.P["D"] = (value & 0x08) > 0
    cpu.P["I"] = (value & 0x04) > 0
    cpu.P["Z"] = (value & 0x02) > 0
    cpu.P["C"] = (value & 0x01) > 0
    cpu.cycles += 4
    cpu.PC += 1

# ジャンプ命令
# JMP命令
def jmp_im16(cpu, mb): # 0x4C
    addr = im16_ads(cpu, mb)
    cpu.PC = addr #mb.mmu_read(addr)
    cpu.cycles += 3

def jmp_iim16(cpu, mb): # 0x6C
    addr = mb.mmu_read(cpu.PC + 1) | mb.mmu_read(cpu.PC + 2) << 8
    addr_l = mb.mmu_read(addr)
    addr_h = mb.mmu_read(addr + 1)
    cpu.PC = mb.mmu_read(addr_l) | mb.mmu_read(addr_h) << 8
    cpu.cycles += 5

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
    cpu.PC = im16_ads(cpu, mb)
    cpu.cycles += 6

# RTS命令
def rts(cpu, mb, ppu): # 0x60
    cpu.SP += 1
    rtn_addr_l = mb.mmu_read(cpu.SP | 0x100)
    cpu.SP += 1
    rtn_addr_h = mb.mmu_read(cpu.SP| 0x100)
    cpu.PC = rtn_addr_l | rtn_addr_h << 8
    cpu.PC += 1 # <-これ重要
    cpu.cycles += 6

# RTI命令
def rti(cpu, mb, ppu): # 0x40
    plp(cpu, mb)
    cpu.SP += 1
    cpu.PC = mb.mmu_read(0x100 | cpu.SP)
    cpu.SP += 1
    cpu.PC = mb.mmu_read(0x100 | cpu.SP) << 8
    cpu.cycles += 6

# 分岐命令
# BCC命令
def bcc(cpu, mb): # 0x90
    if cpu.P['C'] == False:
        value = im8_ads(cpu, mb)
        cpu.PC += -(value & 0x80) | (value & 0x7F) + 2
    else:
        cpu.PC += 2
    cpu.cycles += 2

# BCS命令
def bcs(cpu, mb): # 0xB0
    if cpu.P['C'] == True:
        value = im8_ads(cpu, mb)
        cpu.PC += -(value & 0x80) | (value & 0x7F) + 2
    else:
        cpu.PC += 2
    cpu.cycles += 2

# BEQ命令
def beq(cpu, mb): # 0xF0
    if cpu.P['Z'] == True:
        value = im8_ads(cpu, mb)
        cpu.PC += -(value & 0x80) | (value & 0x7F) + 2
    else:
        cpu.PC += 2
    cpu.cycles += 2

# BMI命令
def bmi(cpu, mb): # 0x30
    if cpu.P['N'] == True:
        value = im8_ads(cpu, mb)
        cpu.PC += -(value & 0x80) | (value & 0x7F) + 2
    else:
        cpu.PC += 2
    cpu.cycles += 2

# BNE命令
def bne(cpu, mb): # 0xD0
    if cpu.P['Z'] == False:
        value = im8_ads(cpu, mb)
        cpu.PC += -(value & 0x80) | (value & 0x7F) + 2
    else:
        cpu.PC += 2
    cpu.cycles += 2

# BPL命令
def bpl(cpu, mb): # 0x10
    if cpu.P['N'] == False:
    #if (cpu.A & 0x80) == 0:
        value = im8_ads(cpu, mb)
        cpu.PC += -(value & 0x80) | (value & 0x7F) + 2
    else:
        cpu.PC += 2
    cpu.cycles += 2

# BVC命令
def bvc(cpu, mb): # 0x50
    if cpu.P['V'] == False:
        value = im8_ads(cpu, mb)
        cpu.PC += -(value & 0x80) | (value & 0x7F) + 2
    else:
        cpu.PC += 2
    cpu.cycles += 2

# BVS命令
def bvs(cpu, mb): # 0x70
    if cpu.P['V'] == True:
        value = im8_ads(cpu, mb)
        cpu.PC += -(value & 0x80) | (value & 0x7F) + 2
    else:
        cpu.PC += 2
    cpu.cycles += 2
# フラグ変更命令
# CLC命令
def clc(cpu, mb): # 0x18
    cpu.cycles += 2
    cpu.PC += 1
    cpu.P['C'] = False

# CLD命令　BCDモードからの復帰らしい
def cld(cpu, mb): # 0xD8
    cpu.cycles += 2
    cpu.PC += 1
    cpu.P['D'] = False

# CLI命令
def cli(cpu, mb): # 0x58
    cpu.cycles += 2
    cpu.PC += 1
    cpu.P['I'] = False

# CLV命令
def clv(cpu, mb): # 0xB8
    cpu.cycles += 2
    cpu.PC += 1
    cpu.P['V'] = False

# SEC命令
def sec(cpu, mb): # 0x38
    cpu.cycles += 2
    cpu.PC += 1
    cpu.P['C'] = True

# SED命令
def sed(cpu, mb): # 0xF8
    cpu.cycles += 2
    cpu.PC += 1
    cpu.P['D'] = True

# SEI命令
def sei(cpu, mb): # 0x78
    cpu.cycles += 2
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
        cpu.PC = mb.mmu_read(0xFFFE) | mb.mmu_read(0xFFFF) << 8

    cpu.cycles += 7

# NOP命令
def nop(cpu, mb): # 0xEA
    cpu.cycles += 2
    cpu.PC += 1
