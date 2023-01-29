# -*- coding:utf-8 -*-

import ctypes
import opcodes as op
import sys
import time
import tkinter
import threading
from PIL import Image, ImageTk, ImageOps

class CPU():
    def __init__(self):
        self.A = 0x00
        self.X = 0x00
        self.Y = 0x00
        self.PC = 0x0000
        self.SP = 0x01FD # debug
        self.P = {
            "N": False, # Negative flag 
            "V": False, # oVerflow flag
            "1": True, # always set
            "B": False, # Break flag
            "D": False, # Decimal flag
            "I": True, # Interrupt flag
            "Z": False, # Zero flag
            "C": False, # Carry flag
        }
        self.cycles = 0
        self.h_line = 0

        self.op_len = [
           #0 1 2 3 4 5 6 7 8 9 A B C D E F
            1,2,1,1,1,2,2,1,1,2,1,1,1,3,3,1, # 0x00
            2,2,1,1,1,2,2,1,1,3,1,1,1,3,3,1, # 0x10
            3,2,1,1,2,2,2,1,1,2,1,1,3,3,3,1, # 0x20
            2,2,1,1,1,2,2,1,1,3,1,1,1,3,3,1, # 0x30
            1,2,1,1,1,2,2,1,1,2,1,1,3,3,3,1, # 0x40
            2,2,1,1,1,2,2,1,1,3,1,1,1,3,3,1, # 0x50
            1,2,1,1,1,2,2,1,1,2,1,1,3,3,3,1, # 0x60
            2,2,1,1,1,2,2,1,1,3,1,1,1,3,3,1, # 0x70
            1,2,1,1,2,2,2,1,1,1,1,1,3,3,1,1, # 0x80
            2,2,1,1,2,2,2,1,1,3,1,1,1,3,3,1, # 0x90
            2,2,2,1,2,2,2,1,1,2,1,1,3,3,3,1, # 0xA0
            2,2,1,1,2,2,2,1,1,3,1,1,3,3,3,1, # 0xB0
            2,2,1,1,2,2,2,1,1,2,1,1,3,3,3,1, # 0xC0
            2,2,1,1,1,2,2,1,1,3,1,1,3,3,3,1, # 0xD0
            2,2,1,1,2,2,2,1,1,2,1,1,1,3,3,1, # 0xE0
            2,2,1,1,1,2,2,1,1,3,1,1,1,3,3,1, # 0xF0
        ]

        self.clk_table = [
           #0 1 2 3 4 5 6 7 8 9 A B C D E F
            7,6,2,8,3,3,5,5,3,2,2,2,4,4,6,6, # 0x00
            2,5,2,8,4,4,6,6,2,4,2,7,4,4,6,7, # 0x10
            6,6,2,8,3,3,5,5,4,2,2,2,4,4,6,6, # 0x20
            2,5,2,8,4,4,6,6,2,4,2,7,4,4,6,7, # 0x30
            6,6,2,8,3,3,5,5,3,2,2,2,3,4,6,6, # 0x40
            2,5,2,8,4,4,6,6,2,4,2,7,4,4,6,7, # 0x50
            6,6,2,8,3,3,5,5,4,2,2,2,5,4,6,6, # 0x60
            2,5,2,8,4,4,6,6,2,4,2,7,4,4,6,7, # 0x70
            2,6,2,6,3,3,3,3,2,2,2,2,4,4,4,4, # 0x80
            2,6,2,6,4,4,4,4,2,4,2,5,5,4,5,5, # 0x90
            2,6,2,6,3,3,3,3,2,2,2,2,4,4,4,4, # 0xA0
            2,5,2,5,4,4,4,4,2,4,2,4,4,4,4,4, # 0xB0
            2,6,2,8,3,3,5,5,2,2,2,2,4,4,6,6, # 0xC0
            2,5,2,8,4,4,6,6,2,4,2,7,4,4,7,7, # 0xD0
            2,6,3,8,3,3,5,5,2,2,2,2,4,4,6,6, # 0xE0
            2,5,2,8,4,4,6,6,2,4,2,7,4,4,7,7, # 0xF0
        ]

    # nestest方式のlog出力
    def debug(self, mb, ppu):
        p = 0x00
        bitmask = 0x80
        for i in self.P.values():
            if i == True:
                p += bitmask
            bitmask >>= 1

        print(str(format(self.PC, '04X')) + "  ", end="")
        print(str(format(mb.mmu_read(self.PC, ppu), '02X')), end = "")
        len = self.op_len[mb.mmu_read(self.PC, ppu)]
        if len == 1:
            print("        ", end = "")
        elif len == 2:
            print(str(" " + format(mb.mmu_read(self.PC + 1, ppu), '02X')), end = "")
            print("     ", end = "")
        elif len == 3:
            print(str(" " + format(mb.mmu_read(self.PC + 1, ppu), '02X')), end = "")
            print(str(" " + format(mb.mmu_read(self.PC + 2, ppu), '02X')), end = "")
            print("  ", end = "")

        print("                                  A:" + str(format(self.A , '02X')), end = "")
        print(" X:" + str(format(self.X , '02X')), end = "")
        print(" Y:" + str(format(self.Y , '02X')), end = "")
        print(" P:" + str(format(p , '02X')), end = "")
        print(" SP:" + str(format(self.SP & 0x0FF , '02X')), end = "")
        print(" PPU:" + str(format(self.h_line , '3d')) +",", end = "")
        print(str(format(self.cycles , '3d')))

    def reset(self, mb, ppu):
        self.PC = mb.mmu_read(0xFFFC, ppu) | mb.mmu_read(0xFFFD, ppu) << 8
        #self.PC = 0xC000

    def add_8(self, a, b):
        return  (a + b) % 0x100

    def sub_8(self, a, b):
        return  (a - b) % 0x100

    def push(self, mb, data, ppu):
        mb.mmu_write(self.SP | 0x100, data, ppu)
        self.SP -= 1

    def fetch(self, mb, ppu):
        return mb.mmu_read(self.PC, ppu)

    def execute(self, opcode, mb, ppu):
        if opcode == 0xA9:
            op.lda_sim8(self, mb, ppu)
        elif opcode == 0xA5:
            op.lda_im8(self, mb, ppu)
        elif opcode == 0xB5:
            op.lda_im8x(self, mb, ppu)
        elif opcode == 0xAD:
            op.lda_im16(self, mb, ppu)
        elif opcode == 0xBD:
            op.lda_im16x(self, mb, ppu)
        elif opcode == 0xB9:
            op.lda_im16y(self, mb, ppu)
        elif opcode == 0xA1:
            op.lda_iim8x(self, mb, ppu)
        elif opcode == 0xB1:
            op.lda_iim8y(self, mb, ppu)
        # LDX命令
        elif opcode == 0xA2:
            op.ldx_sim8(self, mb, ppu)
        elif opcode == 0xA6:
            op.ldx_im8(self, mb, ppu)
        elif opcode == 0xB6:
            op.ldx_im8y(self, mb, ppu)
        elif opcode == 0xAE:
            op.ldx_im16(self, mb, ppu)
        elif opcode == 0xBE:
            op.ldx_im16y(self, mb, ppu)
        # LDY命令
        elif opcode == 0xA0:
            op.ldy_sim8(self, mb, ppu)
        elif opcode == 0xA4:
            op.ldy_im8(self, mb, ppu)
        elif opcode == 0xB4:
            op.ldy_im8x(self, mb, ppu)
        elif opcode == 0xAC:
            op.ldy_im16(self, mb, ppu)
        elif opcode == 0xBC:
            op.ldy_im16x(self, mb, ppu)
        # STA命令
        elif opcode == 0x85:
            op.sta_im8(self, mb, ppu) 
        elif opcode == 0x95:
            op.sta_im8x(self, mb, ppu) 
        elif opcode == 0x8D:
            op.sta_im16(self, mb, ppu)
        elif opcode == 0x9D:
            op.sta_im16x(self, mb, ppu)
        elif opcode == 0x99:
            op.sta_im16y(self, mb, ppu) 
        elif opcode == 0x81:
            op.sta_iim8x(self, mb, ppu)
        elif opcode == 0x91:
            op.sta_iim8y(self, mb, ppu)
        # STX命令
        elif opcode == 0x86:
            op.stx_im8(self, mb, ppu)
        elif opcode == 0x96:
            op.stx_im8y(self, mb, ppu)
        elif opcode == 0x8E:
            op.stx_im16(self, mb, ppu)
        # STY命令
        elif opcode == 0x84:
            op.sty_im8(self, mb, ppu)
        elif opcode == 0x94:
            op.sty_im8x(self, mb, ppu)
        elif opcode == 0x8C:
            op.sty_im16(self, mb, ppu)
        # TAX命令
        elif opcode == 0xAA:
            op.tax(self, mb)
        # TAY命令
        elif opcode == 0xA8:
            op.tay(self, mb)
        # TSX命令
        elif opcode == 0xBA:
            op.tsx(self, mb)
        # TXA命令
        elif opcode == 0x8A:
            op.txa(self, mb)
        # TXS命令
        elif opcode == 0x9A:
            op.txs(self, mb)
        # TYA命令
        elif opcode == 0x98:
            op.tya(self, mb)
        # 算術命令
        # ADC命令
        elif opcode == 0x69:
            op.adc_sim8(self, mb, ppu)
        elif opcode == 0x65:
            op.adc_im8(self, mb, ppu)
        elif opcode == 0x75:
            op.adc_im8x(self, mb, ppu)
        elif opcode == 0x6D:
            op.adc_im16(self, mb, ppu)
        elif opcode == 0x7D:
            op.adc_im16x(self, mb, ppu)
        elif opcode == 0x79:
            op.adc_im16y(self, mb, ppu)
        elif opcode == 0x61:
            op.adc_iim8x(self, mb, ppu)
        elif opcode == 0x71:
            op.adc_iim8y(self, mb, ppu)
        # AND命令
        elif opcode == 0x29:
            op.and_sim8(self, mb, ppu)
        elif opcode == 0x25:
            op.and_im8(self, mb, ppu)
        elif opcode == 0x35:
            op.and_im8x(self, mb, ppu)
        elif opcode == 0x2D:
            op.and_im16(self, mb, ppu)
        elif opcode == 0x3D:
            op.and_im16x(self, mb, ppu)
        elif opcode == 0x39:
            op.and_im16y(self, mb, ppu)
        elif opcode == 0x21:
            op.and_iim8x(self, mb, ppu)
        elif opcode == 0x31:
            op.and_iim8y(self, mb, ppu)
        # ASL命令
        elif opcode == 0x0A:
            op.asl_acc(self, mb)
        elif opcode == 0x06:
            op.asl_im8(self, mb, ppu)
        elif opcode == 0x16:
            op.asl_im8x(self, mb, ppu)
        elif opcode == 0x0E:
            op.asl_im16(self, mb, ppu)
        elif opcode == 0x1E:
            op.asl_im16x(self, mb, ppu)
        # BIT命令
        elif opcode == 0x24:
            op.bit_im8(self, mb, ppu)
        elif opcode == 0x2C:
            op.bit_im16(self, mb, ppu)           
        # CMP命令
        elif opcode == 0xC9:
            op.cmp_sim8(self, mb, ppu)
        elif opcode == 0xC5:
            op.cmp_im8(self, mb, ppu)
        elif opcode == 0xD5:
            op.cmp_im8x(self, mb, ppu)
        elif opcode == 0xCD:
            op.cmp_im16(self, mb, ppu)
        elif opcode == 0xDD:
            op.cmp_im16x(self, mb, ppu)
        elif opcode == 0xD9:
            op.cmp_im16y(self, mb, ppu)
        elif opcode == 0xC1:
            op.cmp_iim8x(self, mb, ppu)
        elif opcode == 0xD1:
            op.cmp_iim8y(self, mb, ppu)
        # CPX命令
        elif opcode == 0xE0:
            op.cpx_sim8(self, mb, ppu)
        elif opcode == 0xE4:
            op.cpx_im8(self, mb, ppu)
        elif opcode == 0xEC:
            op.cpx_im16(self, mb, ppu)
        # CPY命令
        elif opcode == 0xC0:
            op.cpy_sim8(self, mb, ppu)
        elif opcode == 0xC4:
            op.cpy_im8(self, mb, ppu)
        elif opcode == 0xCC:
            op.cpy_im16(self, mb, ppu)
        # DEC命令
        elif opcode == 0xC6:
            op.dec_im8(self, mb, ppu)
        elif opcode == 0xD6:
            op.dec_im8x(self, mb, ppu)
        elif opcode == 0xCE:
            op.dec_im16(self, mb, ppu)
        elif opcode == 0xDE:
            op.dec_im16x(self, mb, ppu)
        # DEX命令
        elif opcode == 0xCA:
            op.dex(self, mb) 
        # DEY命令
        elif opcode == 0x88:
            op.dey(self, mb) 
        # EOR命令
        elif opcode == 0x49:
            op.eor_sim8(self, mb, ppu)
        elif opcode == 0x45:
            op.eor_im8(self, mb, ppu)
        elif opcode == 0x55:
            op.eor_im8x(self, mb, ppu)
        elif opcode == 0x4D:
            op.eor_im16(self, mb, ppu)
        elif opcode == 0x5D:
            op.eor_im16x(self, mb, ppu)
        elif opcode == 0x59:
            op.eor_im16y(self, mb, ppu)
        elif opcode == 0x41:
            op.eor_iim8x(self, mb, ppu)
        elif opcode == 0x51:
            op.eor_iim8y(self, mb, ppu)
        # INC命令
        elif opcode == 0xE6:
            op.inc_im8(self, mb, ppu)
        elif opcode == 0xF6:
            op.inc_im8x(self, mb, ppu)
        elif opcode == 0xEE:
            op.inc_im16(self, mb, ppu)
        elif opcode == 0xFE:
            op.inc_im16x(self, mb, ppu)
        # INX命令
        elif opcode == 0xE8:
            op.inx(self, mb)
        # INY命令
        elif opcode == 0xC8:
            op.iny(self, mb)
        # LSR命令
        elif opcode == 0x4A:
            op.lsr_acc(self, mb)
        elif opcode == 0x46:
            op.lsr_im8(self, mb, ppu)
        elif opcode == 0x56:
            op.lsr_im8x(self, mb, ppu)
        elif opcode == 0x4E:
            op.lsr_im16(self, mb, ppu)
        elif opcode == 0x5E:
            op.lsr_im16x(self, mb, ppu)
        # ORA命令
        elif opcode == 0x09:
            op.ora_sim8(self, mb, ppu)
        elif opcode == 0x05:
            op.ora_im8(self, mb, ppu)
        elif opcode == 0x15:
            op.ora_im8x(self, mb, ppu)
        elif opcode == 0x0D:
            op.ora_im16(self, mb, ppu)
        elif opcode == 0x1D:
            op.ora_im16x(self, mb, ppu)
        elif opcode == 0x19:
            op.ora_im16y(self, mb, ppu)
        elif opcode == 0x01:
            op.ora_iim8x(self, mb, ppu)
        elif opcode == 0x11:
            op.ora_iim8y(self, mb, ppu)
        # ROL命令
        elif opcode == 0x2A:
            op.rol_acc(self, mb)
        elif opcode == 0x26:
            op.rol_im8(self, mb, ppu)
        elif opcode == 0x36:
            op.rol_im8x(self, mb, ppu)
        elif opcode == 0x2E:
            op.rol_im16(self, mb, ppu)
        elif opcode == 0x3E:
            op.rol_im16x(self, mb, ppu)
        # ROR命令
        elif opcode == 0x6A:
            op.ror_acc(self, mb)
        elif opcode == 0x66:
            op.ror_im8(self, mb, ppu)
        elif opcode == 0x76:
            op.ror_im8x(self, mb, ppu)
        elif opcode == 0x6E:
            op.ror_im16(self, mb, ppu)
        elif opcode == 0x7E:
            op.ror_im16x(self, mb, ppu)
        # SBC命令
        elif opcode == 0xE9:
            op.sbc_sim8(self, mb, ppu)
        elif opcode == 0xE5:
            op.sbc_im8(self, mb, ppu)
        elif opcode == 0xF5:
            op.sbc_im8x(self, mb, ppu)
        elif opcode == 0xED:
            op.sbc_im16(self, mb, ppu)
        elif opcode == 0xFD:
            op.sbc_im16x(self, mb, ppu)
        elif opcode == 0xF9:
            op.sbc_im16y(self, mb, ppu)
        elif opcode == 0xE1:
            op.sbc_iim8x(self, mb, ppu)
        elif opcode == 0xF1:
            op.sbc_iim8y(self, mb, ppu)
        # スタック命令
        # PHA命令
        elif opcode == 0x48:
            op.pha(self, mb, ppu)
        # PHP命令
        elif opcode == 0x08:
            op.php(self, mb, ppu)
        # PLA命令
        elif opcode == 0x68:
            op.pla(self, mb, ppu)
        # PLP命令
        elif opcode == 0x28:
            op.plp(self, mb, ppu)
        # ジャンプ命令
        # JMP命令
        elif opcode == 0x4C:
            op.jmp_im16(self, mb, ppu)
        elif opcode == 0x6C:
            op.jmp_iim8(self, mb, ppu)
        # JSR命令
        elif opcode == 0x20:
            op.jsr(self, mb, ppu)
        # RTS命令
        elif opcode == 0x60:
            op.rts(self, mb, ppu)
        # RTI命令
        elif opcode == 0x40:
            op.rti(self, mb, ppu)
        # 分岐命令
        # BCC命令
        elif opcode == 0x90:
            op.bcc(self, mb, ppu)
        # BCS命令
        elif opcode == 0xB0:
            op.bcs(self, mb, ppu)
        # BEQ命令
        elif opcode == 0xF0:
            op.beq(self, mb, ppu)
        # BMI命令
        elif opcode == 0x30:
            op.bmi(self, mb, ppu)
        # BNE命令
        elif opcode == 0xD0:
            op.bne(self, mb, ppu)
        # BPL命令
        elif opcode == 0x10:
            op.bpl(self, mb, ppu)
        # BVC命令
        elif opcode == 0x50:
            op.bvc(self, mb, ppu)
        # BVS命令
        elif opcode == 0x70:
            op.bvs(self, mb, ppu)
        # フラグ変更命令
        # CLC命令
        elif opcode == 0x18:
            op.clc(self, mb)
        # CLD命令　BCDモードからの復帰らしい
        elif opcode == 0xD8:
            op.cld(self, mb)
        # CLI命令
        elif opcode == 0x58:
            op.cli(self, mb)
        # CLV命令
        elif opcode == 0xB8:
            op.clv(self, mb)
        # SEC命令
        elif opcode == 0x38:
            op.sec(self, mb)
        # SED命令
        elif opcode == 0xF8:
            op.sed(self, mb)
        # SEI命令
        elif opcode == 0x78:
            op.sei(self, mb)
        # その他の命令
        # BRK命令
        elif opcode == 0x00:
            op.brk(self, mb, ppu)
        # NOP命令
        elif opcode == 0xEA:
            op.nop(self, mb)
        elif opcode == 0x04:
            op.undef_nop1(self, mb)
        elif opcode == 0x44:
            op.undef_nop1(self, mb)
        elif opcode == 0x64:
            op.undef_nop1(self, mb)
        elif opcode == 0x0C:
            op.undef_nop2(self, mb)
        elif opcode == 0x14:
            op.undef_nop1(self, mb)
        elif opcode == 0x34:
            op.undef_nop1(self, mb)
        elif opcode == 0x54:
            op.undef_nop1(self, mb)
        elif opcode == 0x74:
            op.undef_nop1(self, mb)
        elif opcode == 0xD4:
            op.undef_nop1(self, mb)
        elif opcode == 0xF4:
            op.undef_nop1(self, mb)
        elif opcode == 0x1A:
            op.nop(self, mb)
        elif opcode == 0x3A:
            op.nop(self, mb)
        elif opcode == 0x5A:
            op.nop(self, mb)
        elif opcode == 0x7A:
            op.nop(self, mb)
        elif opcode == 0xDA:
            op.nop(self, mb)
        elif opcode == 0xFA:
            op.nop(self, mb)
        elif opcode == 0x80:
            op.undef_nop1(self, mb)
        elif opcode == 0x1C:
            op.undef_nop2(self, mb)
        elif opcode == 0x3C:
            op.undef_nop2(self, mb)
        elif opcode == 0x5C:
            op.undef_nop2(self, mb)
        elif opcode == 0x7C:
            op.undef_nop2(self, mb)
        elif opcode == 0xDC:
            op.undef_nop2(self, mb)
        elif opcode == 0xFC:
            op.undef_nop2(self, mb)
        # LAX命令
        elif opcode == 0xA3:
            op.lax_iim8x(self, mb, ppu)
        elif opcode == 0xA7:
            op.lax_im8(self, mb, ppu)
        elif opcode == 0xAF:
            op.lax_im16(self, mb, ppu)
        elif opcode == 0xB3:
            op.lax_iim8y(self, mb, ppu)
        elif opcode == 0xB7:
            op.lax_im8y(self, mb, ppu)
        elif opcode == 0xBF:
            op.lax_im16y(self, mb, ppu)
        # SAX命令
        elif opcode == 0x83:
            op.sax_iim8x(self, mb, ppu)
        elif opcode == 0x87:
            op.sax_im8(self, mb, ppu)
        elif opcode == 0x8F:
            op.sax_im16(self, mb, ppu)
        elif opcode == 0x97:
            op.sax_im8x(self, mb, ppu)
        # 非公式SBC命令
        elif opcode == 0xEB:
            op.sbc_sim8(self, mb, ppu)
        else:
            print("is that right opcode?")
            print('opcode:{:#04X}'.format(opcode))
            sys.exit()

class MotherBoard:
    def __init__(self):
        self.WRAM    = [0x00] * 0x0800 # $0000～$07FF
        self.EXROM1  = [0x00] * 0x1FE0 # $4020～$5FFF
        self.EXROM2  = [0x00] * 0x2000 # $6000～$7FFF
        self.PRGROM1 = [0x00] * 0x4000 # $8000～$BFFF
        self.PRGROM2 = [0x00] * 0x4000 # $C000～$FFFF

        self.PPUC1    = 0x00 # PPU制御レジスタ１@0x2000
        self.PPUC2    = 0x00 # PPU制御レジスタ２@0x2001
        self.PPUST    = 0x00 # PPUステータスレジスタ@0x2002
        self.OAMAD    = 0x00 # 書き込むsprite領域のアドレス @0x2003
        self.OAMDATA  = 0x00 # sprite領域のデータ @0x2004
        self.PPUSCR   = 0x00 # 背景スクロール値 @0x2005
        self.VRAMAD   = 0x0000 # 書き込むPPUメモリ領域のアドレス@0x2006
        self.F_VRAMAD = True # True:上位アドレス　False:下位アドレス
        self.VRAMAC   = 0x00 # PPUメモリ領域のデータ@0x2007

        self.JOYPAD1  = 0x00 # @0x4016
        self.JOYPAD2  = 0x00 # @0x4017

        self.joypad_cnt = 0
        self.joypad_read = 0

        self.VH_flag = True # True :vertical False: horizontal

        self.v_scr = 0
        self.h_scr = 0
        self.scr_f = True # True H False V

    def rom_read(self, f, ppu):
        nes_header = f.read(16)

        if nes_header[4] == 1: # nes_header[4] is PRO_ROM size
            for i in range(0x4000):
                self.PRGROM2[i] = int.from_bytes(f.read(1), byteorder = sys.byteorder)
        elif nes_header[4] == 2: # nes_header[4] is PRO_ROM size
            for i in range(0x4000):
                self.PRGROM1[i] = int.from_bytes(f.read(1), byteorder = sys.byteorder)
            for i in range(0x4000):
                self.PRGROM2[i] = int.from_bytes(f.read(1), byteorder = sys.byteorder)
        else:
            print("not yet! 1")
            print(nes_header[4])
            sys.exit()

        if nes_header[5] == 1:
            for i in range(0x1000):
                ppu.PTABLE_H[i] = int.from_bytes(f.read(1), byteorder = sys.byteorder)
        else:
            print("not yet! 2")
            print(nes_header[5])
            sys.exit()

        if nes_header[6] & 0x01 == 1:
            self.VH_flag = True
        else:
            self.VH_flag = False

    def joypad(self):
        global key
        if self.joypad_cnt == 0:
            self.joypad_cnt += 1
            self.joypad_cnt %= 8
            if key == 65: # a
                key = 0
                return 1 #self.JOYPAD1 | 0x01
            else:
                return 0 #self.JOYPAD1 & 0xFE
        elif self.joypad_cnt == 1:
            self.joypad_cnt += 1
            self.joypad_cnt %= 8
            if key == 83: # s
                key = 0
                return 1 # | 0x01
            else:
                return 0 #self.JOYPAD1 & 0xFE
        elif self.joypad_cnt == 2:
            self.joypad_cnt += 1
            self.joypad_cnt %= 8
            if key == 87: # w
                key = 0
                return 1 # 0x01
            else:
                return 0 #self.JOYPAD1 & 0xFE
        elif self.joypad_cnt == 3:
            self.joypad_cnt += 1
            self.joypad_cnt %= 8
            if key == 81: # q
                key = 0
                return 1 # | 0x01
            else:
                return 0 #self.JOYPAD1 & 0xFE
        elif self.joypad_cnt == 4:
            self.joypad_cnt += 1
            self.joypad_cnt %= 8
            if key == 38: # up
                key = 0
                return 1 # | 0x01
            else:
                return 0 #self.JOYPAD1 & 0xFE
        elif self.joypad_cnt == 5:
            self.joypad_cnt += 1
            self.joypad_cnt %= 8
            if key == 40: # down
                key = 0
                return 1 # | 0x01
            else:
                return 0 #self.JOYPAD1 & 0xFE
        elif self.joypad_cnt == 6:
            self.joypad_cnt += 1
            self.joypad_cnt %= 8
            if key == 37: # left
                key = 0
                return 1 # | 0x01
            else:
                return 0 #self.JOYPAD1 & 0xFE
        elif self.joypad_cnt == 7:
            self.joypad_cnt += 1
            self.joypad_cnt %= 8
            if key == 39: # right
                key = 0
                return 1 # | 0x01
            else:
                return 0 #self.JOYPAD1 & 0xFE
        else:
            return 0 #self.JOYPAD1 & 0xFE

    def mmu_read(self, addr, ppu):
        if 0x0000 <= addr <= 0x07FF:
            return self.WRAM[addr - 0x0000]
        elif 0x0800 <= addr <= 0x0FFF:
            return self.WRAM[addr - 0x0800]
        elif 0x1000 <= addr <= 0x17FF:
            return self.WRAM[addr - 0x1000]
        elif 0x1800 <= addr <= 0x1FFF:
            return self.WRAM[addr - 0x1800]
        # PPU I/O
        elif 0x2000 <= addr <= 0x3FFF:
            if addr & 0x0007 == 0x0002:
                tmp_PPUST = self.PPUST
                self.PPUST &= 0x7F # 破壊的変更を伴う
                self.scr_f = True
                self.F_VRAMAD = True
                return tmp_PPUST
            elif addr & 0x0007 == 0x0004:
                return self.OAMDATA
            elif addr & 0x0007 == 0x0007:
                if self.PPUC1 & 0x04 > 0:
                    self.VRAMAD += 32
                else:
                    self.VRAMAD += 1
                return ppu.read(self.VRAMAD, ppu)
        # APU I/O PAD
        elif 0x4000 <= addr <= 0x401F:
            if addr == 0x4016:
                if self.joypad_read == 0:
                    return self.JOYPAD1
                elif self.joypad_read == 1:
                    self.joypad_read = 0
                    return self.JOYPAD1
                elif self.joypad_read == 2:
                    key = 0
                    return self.joypad()
                else:
                    self.joypad_read = 0
                    return self.JOYPAD1
            elif addr == 0x4017:
                return 0x00 # 2pコントローラは未実装
        # ROM
        elif 0x4020 <= addr <= 0x5FFF:
            return self.EXROM1[addr - 0x4020]
        elif 0x6000 <= addr <= 0x7FFF:
            return self.EXROM2[addr - 0x6000]
        elif 0x8000 <= addr <= 0xBFFF:
            return self.PRGROM1[addr - 0x8000]
        elif 0xC000 <= addr <= 0xFFFF:
            return self.PRGROM2[addr - 0xC000]

    def mmu_write(self, addr, data, ppu):
        if 0x0000 <= addr <= 0x07FF:
            self.WRAM[addr - 0x0000] = data
        elif 0x0800 <= addr <= 0x0FFF:
            self.WRAM[addr - 0x0800] = data
        elif 0x1000 <= addr <= 0x17FF:
            self.WRAM[addr - 0x1000] = data
        elif 0x1800 <= addr <= 0x1FFF:
            self.WRAM[addr - 0x1800] = data
        # PPU I/O
        elif 0x2000 <= addr <= 0x3FFF:
            if addr & 0x0007 == 0x0000:
                self.PPUC1 = data
            elif addr & 0x0007 == 0x0001:
                self.PPUC2 = data
            elif addr & 0x0007 == 0x0003:
                self.OAMAD = data
            elif addr & 0x0007 == 0x0004:
                ppu.SPDATA[self.OAMAD] = data
            elif addr & 0x0007 == 0x0005:
                if self.scr_f:
                    self.scr_f = False
                    self.PPUSCR = data
                    self.h_scr = data
                else:
                    self.scr_f = True
                    self.PPUSCR = data
                    self.v_scr = data           
            elif addr & 0x0007 == 0x0006:
                #if self.F_VRAMAD:
                if self.scr_f: # 内部的には0x2005と状態を共有している
                    self.VRAMAD &= 0x00FF
                    self.VRAMAD |= (data << 8)
                    #self.F_VRAMAD = False
                    self.scr_f = False
                else:
                    self.VRAMAD &= 0xFF00
                    self.VRAMAD |= data
                    #self.F_VRAMAD = True
                    self.scr_f = True
            elif addr & 0x0007 == 0x0007:
                ppu.write(self.VRAMAD, data, self)
                if self.PPUC1 & 0x04 > 0:
                    self.VRAMAD += 32
                else:
                    self.VRAMAD += 1

        # APU I/O PAD
        elif 0x4000 <= addr <= 0x401F:
            if addr == 0x4014:
                # DMA
                for i in range(0x100):
                    ppu.SPDATA[i] = self.WRAM[data << 8 | i]
                global tmp_clk
                tmp_clk += 514
            elif addr == 0x4016:
                self.JOYPAD1 = data
                if self.joypad_read == 0:
                    if data & 0x01 == 0x01:
                        self.joypad_read = 1
                elif self.joypad_read == 1:
                    if data & 0x01 == 0x00:
                        self.joypad_read = 2
                    else:
                        self.joypad_read = 0
                elif self.joypad_read == 2:
                    self.joypad_read = 0

            elif addr == 0x4017:
                self.JOYPAD2 = data

        # PROGROM fof debug only
        elif 0x8000 <= addr <= 0xBFFF:
            self.PRGROM1[addr - 0x8000] = data
        elif 0xC000 <= addr <= 0xFFFF:
            self.PRGROM2[addr - 0xC000] = data

class PPU():
    def __init__(self):
        self.PTABLE_H = [0x00] * 0x1000 # $0000～$0FFF パターンテーブルHIGH
        self.PTABLE_L = [0x00] * 0x1000 # $1000～$1FFF パターンテーブルLOW
        self.DP1_NTBL = [0x00] * 0x03C0 # $2000～$23BF 画面１ネームテーブル
        self.DP1_ATBL = [0x00] * 0x0040 # $23C0～$23FF 画面１属性テーブル
        self.DP2_NTBL = [0x00] * 0x03C0 # $2400～$27BF 画面２ネームテーブル
        self.DP2_ATBL = [0x00] * 0x0040 # $27C0～$27FF 画面２属性テーブル
        self.BG_PTBL  = [0x00] * 0x0010 # $3F00～$3F0F BGパレットテーブル
        self.SP_PTBL  = [0x00] * 0x0010 # $3F10～$3F1F スプライトパレットテーブル

        self.SPDATA = [0x00] * 0x100 # スプライト用データ、アドレス不明
             
        self.img_from_DP1 = Image.new('RGBA', (8, 8), (0, 0, 0, 0xFF))
        self.img_from_DP2 = Image.new('RGBA', (8, 8), (0, 0, 0, 0xFF))
        self.bitmap = Image.new('RGBA', (256, 240), (0, 0, 0, 0xFF))
        self.bg = Image.new('RGBA', (512, 480), (0, 0, 0, 0xFF))
        self.ppu_cycle = 0x00

        # NESの色情報
        self.colors = [
                (0x80, 0x80, 0x80, 0xFF), (0x00, 0x3D, 0xA6, 0xFF), (0x00, 0x12, 0xB0, 0xFF), (0x44, 0x00, 0x96, 0xFF), # ~  3
                (0xA1, 0x00, 0x5E, 0xFF), (0xC7, 0x00, 0x28, 0xFF), (0xBA, 0x06, 0x00, 0xFF), (0x8C, 0x17, 0x00, 0xFF), # ~  7
                (0x5C, 0x2F, 0x00, 0xFF), (0x10, 0x45, 0x00, 0xFF), (0x05, 0x4A, 0x00, 0xFF), (0x00, 0x47, 0x2E, 0xFF), # ~ 11
                (0x00, 0x41, 0x66, 0xFF), (0x00, 0x00, 0x00, 0xFF), (0x05, 0x05, 0x05, 0xFF), (0x05, 0x05, 0x05, 0xFF), # ~ 15
                (0xC7, 0xC7, 0xC7, 0xFF), (0x00, 0x77, 0xFF, 0xFF), (0x21, 0x55, 0xFF, 0xFF), (0x82, 0x37, 0xFA, 0xFF), # ~ 19
                (0xEB, 0x2F, 0xB5, 0xFF), (0xFF, 0x29, 0x50, 0xFF), (0xFF, 0x22, 0x00, 0xFF), (0xD6, 0x32, 0x00, 0xFF), # ~ 23
                (0xC4, 0x62, 0x00, 0xFF), (0x35, 0x80, 0x00, 0xFF), (0x05, 0x8F, 0x00, 0xFF), (0x00, 0x8A, 0x55, 0xFF), # ~ 27
                (0x00, 0x99, 0xCC, 0xFF), (0x21, 0x21, 0x21, 0xFF), (0x09, 0x09, 0x09, 0xFF), (0x09, 0x09, 0x09, 0xFF), # ~ 31
                (0xFF, 0xFF, 0xFF, 0xFF), (0x0F, 0xD7, 0xFF, 0xFF), (0x69, 0xA2, 0xFF, 0xFF), (0xD4, 0x80, 0xFF, 0xFF), # ~ 35
                (0xFF, 0x45, 0xF3, 0xFF), (0xFF, 0x61, 0x8B, 0xFF), (0xFF, 0x88, 0x33, 0xFF), (0xFF, 0x9C, 0x12, 0xFF), # ~ 39
                (0xFA, 0xBC, 0x20, 0xFF), (0x9F, 0xE3, 0x0E, 0xFF), (0x2B, 0xF0, 0x35, 0xFF), (0x0C, 0xF0, 0xA4, 0xFF), # ~ 43
                (0x05, 0xFB, 0xFF, 0xFF), (0x5E, 0x5E, 0x5E, 0xFF), (0x0D, 0x0D, 0x0D, 0xFF), (0x0D, 0x0D, 0x0D, 0xFF), # ~ 47
                (0xFF, 0xFF, 0xFF, 0xFF), (0xA6, 0xFC, 0xFF, 0xFF), (0xB3, 0xEC, 0xFF, 0xFF), (0xDA, 0xAB, 0xEB, 0xFF), # ~ 51
                (0xFF, 0xA8, 0xF9, 0xFF), (0xFF, 0xAB, 0xB3, 0xFF), (0xFF, 0xD2, 0xB0, 0xFF), (0xFF, 0xEF, 0xA6, 0xFF), # ~ 55
                (0xFF, 0xF7, 0x9C, 0xFF), (0xD7, 0xE8, 0x95, 0xFF), (0xA6, 0xED, 0xAF, 0xFF), (0xA2, 0xF2, 0xDA, 0xFF), # ~ 59
                (0x99, 0xFF, 0xFC, 0xFF), (0xDD, 0xDD, 0xDD, 0xFF), (0x11, 0x11, 0x11, 0xFF), (0x11, 0x11, 0x11, 0xFF), # ~ 63
        ]

    def write(self, addr, data, mb):
        if 0x0000 <= addr <= 0x0FFF:
            self.PTABLE_H[addr - 0x0000] = data
        elif 0x1000 <= addr <= 0x1FFF:
            self.PTABLE_L[addr - 0x1000] = data
        elif 0x2000 <= addr <= 0x23BF: # 1
            self.DP1_NTBL[addr - 0x2000] = data
        elif 0x23C0 <= addr <= 0x23FF: # 1
            self.DP1_ATBL[addr - 0x23C0] = data
        elif 0x2400 <= addr <= 0x27BF: # 2
            if mb.VH_flag == True:
                self.DP2_NTBL[addr - 0x2400] = data
            else:
                self.DP1_NTBL[addr - 0x2400] = data
        elif 0x27C0 <= addr <= 0x27FF: # 2
            if mb.VH_flag == True:
                self.DP2_ATBL[addr - 0x27C0] = data
            else:
                self.DP1_ATBL[addr - 0x27C0] = data
        elif 0x2800 <= addr <= 0x2BBF: # 3
            if mb.VH_flag == True:
                self.DP1_NTBL[addr - 0x2800] = data
            else:
                self.DP2_NTBL[addr - 0x2800] = data
        elif 0x2BC0 <= addr <= 0x2BFF: # 3
            if mb.VH_flag == True:
                self.DP1_ATBL[addr - 0x2BC0] = data
            else:
                self.DP2_ATBL[addr - 0x2BC0] = data
        elif 0x2C00 <= addr <= 0x2FBF: # 4
            self.DP2_NTBL[addr - 0x2C00] = data
        elif 0x2FC0 <= addr <= 0x2FFF: # 4
            self.DP2_ATBL[addr - 0x2FC0] = data
        elif 0x3000 <= addr <= 0x3EFF:
            self.write(addr & 0xFEFF, data, mb)
        elif 0x3F00 <= addr <= 0x3FFF:
            if addr == 0x3F00 or addr == 0x3F10:
                self.BG_PTBL[0x00] = data
                self.SP_PTBL[0x00] = data
            elif addr == 0x3F04 or addr == 0x3F14:
                self.BG_PTBL[0x04] = data
                self.SP_PTBL[0x04] = data
            elif addr == 0x3F08 or addr == 0x3F18:
                self.BG_PTBL[0x08] = data
                self.SP_PTBL[0x08] = data
            elif addr == 0x3F0C or addr == 0x3F1C:
                self.BG_PTBL[0x0C] = data
                self.SP_PTBL[0x0C] = data
            elif addr <= 0x3F1F:
                if addr & 0x0010 == 0:
                    self.BG_PTBL[addr & 0x0F] = data
                else:
                    self.SP_PTBL[addr & 0x0F] = data
            else:
                self.write(addr & 0xFF1F, data, mb)
        else:
            print("ppu write error!")
            print("addr:" + str(format(addr , '04X')))
            print("data:" + str(format(data , '02X')))
            sys.exit()

    def read(self, addr, mb):
        if 0x0000 <= addr <= 0x0FFF:
            return self.PTABLE_H[addr - 0x0000]
        elif 0x1000 <= addr <= 0x1FFF:
            return self.PTABLE_L[addr - 0x1000]
        elif 0x2000 <= addr <= 0x23BF:
            return self.DP1_NTBL[addr - 0x2000]
        elif 0x23C0 <= addr <= 0x23FF:
            return self.DP1_ATBL[addr - 0x23C0]
        elif 0x2400 <= addr <= 0x27BF:
            if mb.VH_flag == True:
                return self.DP2_NTBL[addr - 0x2400]
            else:
                return self.DP1_NTBL[addr - 0x2400]
        elif 0x27C0 <= addr <= 0x27FF:
            if mb.VH_flag == True:
                return self.DP2_ATBL[addr - 0x27C0]
            else:
                return self.DP1_ATBL[addr - 0x27C0]
        elif 0x2800 <= addr <= 0x2BBF:
            if mb.VH_flag == True:
                return self.DP1_NTBL[addr - 0x2800]
            else:
                return self.DP2_NTBL[addr - 0x2800]
        elif 0x2BC0 <= addr <= 0x2BFF:
            if mb.VH_flag == True:
                return self.DP1_ATBL[addr - 0x2BC0]
            else:
                return self.DP2_ATBL[addr - 0x2BC0]
        elif 0x2C00 <= addr <= 0x2FBF:
            return self.DP2_NTBL[addr - 0x2C00]
        elif 0x2FC0 <= addr <= 0x2FFF:
            return self.DP2_ATBL[addr - 0x2FC0]
        elif 0x3000 <= addr <= 0x3EFF:
            return self.read(addr & 0xFEFF, mb)
        elif 0x3F00 <= addr <= 0x3FFF:
            if addr & 0x0010 == 0:
                return self.BG_PTBL[addr & 0x0F]
            else:
                return self.SP_PTBL[addr & 0x0F]
        else:
            print("ppu read error!")
            print("addr:" + str(format(addr , '04X')))
            sys.exit()

    # not embedded color pallet yet
    def get_tile(self, PPUC1_bit4, x, y, DP):

        plt_blk = x >> 2 | (y >> 2) << 3
        plt_bit = (x & 0x02 >> 1 | y & 0x02) << 1

        if DP:
            tile_num = self.DP1_NTBL[x | y << 5] << 4
            plt_num = self.DP1_ATBL[plt_blk] & (0x03 << plt_bit) >> plt_bit
        else:
            tile_num = self.DP2_NTBL[x | y << 5] << 4
            plt_num = self.DP2_ATBL[plt_blk] & (0x03 << plt_bit) >> plt_bit

        if plt_num == 0:
            color_plt = [(0, 0, 0, 0), self.colors[self.BG_PTBL[1]], self.colors[self.BG_PTBL[2]], self.colors[self.BG_PTBL[3]]]
        else:
            plt_num <<= 2
            color_plt = [(0, 0, 0, 0), self.colors[self.BG_PTBL[plt_num | 1]], self.colors[self.BG_PTBL[plt_num | 2]], self.colors[self.BG_PTBL[plt_num | 3]]]

        data_byte = [color_plt[0]] * 64

        if PPUC1_bit4:
            for yy in range(8):
                tmp_yy = yy << 3
                tmp_PTABLE_L = self.PTABLE_L[tile_num | yy]
                tmp_PTABLE_L_8 = self.PTABLE_L[tile_num | yy | 8]
                color = int(tmp_PTABLE_L & 0x80 > 0)
                color += int(tmp_PTABLE_L_8 & 0x80 > 0) << 1
                if color:
                    data_byte[tmp_yy | 0] = color_plt[color]
                color = int(tmp_PTABLE_L & 0x40 > 0)
                color += int(tmp_PTABLE_L_8 & 0x40 > 0) << 1
                if color:
                    data_byte[tmp_yy | 1] = color_plt[color]
                color = int(tmp_PTABLE_L & 0x20 > 0)
                color += int(tmp_PTABLE_L_8 & 0x20 > 0) << 1
                if color:
                    data_byte[tmp_yy | 2] = color_plt[color]
                color = int(tmp_PTABLE_L & 0x10 > 0)
                color += int(tmp_PTABLE_L_8 & 0x10 > 0) << 1
                if color:
                    data_byte[tmp_yy | 3] = color_plt[color]
                color = int(tmp_PTABLE_L & 0x08 > 0)
                color += int(tmp_PTABLE_L_8 & 0x08 > 0) << 1
                if color:
                    data_byte[tmp_yy | 4] = color_plt[color]
                color = int(tmp_PTABLE_L & 0x04 > 0)
                color += int(tmp_PTABLE_L_8 & 0x04 > 0) << 1
                if color:
                    data_byte[tmp_yy | 5] = color_plt[color]
                color = int(tmp_PTABLE_L & 0x02 > 0)
                color += int(tmp_PTABLE_L_8 & 0x02 > 0) << 1
                if color:
                    data_byte[tmp_yy | 6] = color_plt[color]
                color = int(tmp_PTABLE_L & 0x01 > 0)
                color += int(tmp_PTABLE_L_8 & 0x01 > 0) << 1
                if color:
                    data_byte[tmp_yy | 7] = color_plt[color]
        else:
            for yy in range(8):
                tmp_yy = yy << 3
                tmp_PTABLE_H = self.PTABLE_H[tile_num | yy]
                tmp_PTABLE_H_8 = self.PTABLE_H[tile_num | yy | 8]
                color = int(tmp_PTABLE_H & 0x80 > 0)
                color += int(tmp_PTABLE_H_8 & 0x80 > 0) << 1
                if color:
                    data_byte[tmp_yy | 0] = color_plt[color]
                color = int(tmp_PTABLE_H & 0x40 > 0)
                color += int(tmp_PTABLE_H_8 & 0x40 > 0) << 1
                if color:
                    data_byte[tmp_yy | 1] = color_plt[color]
                color = int(tmp_PTABLE_H & 0x20 > 0)
                color += int(tmp_PTABLE_H_8 & 0x20 > 0) << 1
                if color:
                    data_byte[tmp_yy | 2] = color_plt[color]
                color = int(tmp_PTABLE_H & 0x10 > 0)
                color += int(tmp_PTABLE_H_8 & 0x10 > 0) << 1
                if color:
                    data_byte[tmp_yy | 3] = color_plt[color]
                color = int(tmp_PTABLE_H & 0x08 > 0)
                color += int(tmp_PTABLE_H_8 & 0x08 > 0) << 1
                if color:
                    data_byte[tmp_yy | 4] = color_plt[color]
                color = int(tmp_PTABLE_H & 0x04 > 0)
                color += int(tmp_PTABLE_H_8 & 0x04 > 0) << 1
                if color:
                    data_byte[tmp_yy | 5] = color_plt[color]
                color = int(tmp_PTABLE_H & 0x02 > 0)
                color += int(tmp_PTABLE_H_8 & 0x02 > 0) << 1
                if color:
                    data_byte[tmp_yy | 6] = color_plt[color]
                color = int(tmp_PTABLE_H & 0x01 > 0)
                color += int(tmp_PTABLE_H_8 & 0x01 > 0) << 1
                if color:
                    data_byte[tmp_yy | 7] = color_plt[color]
        return data_byte

    def show_NTBL(self, mb, h_line):
        DP1 = True
        DP2 = False
        PPUC1_bit4 = mb.PPUC1 & 0x10 > 0
        y = h_line >> 3

        if mb.VH_flag:
            for x in range(32):
                self.img_from_DP1.putdata(self.get_tile(PPUC1_bit4, x, y, DP1))
                self.img_from_DP2.putdata(self.get_tile(PPUC1_bit4, x, y, DP2))
                self.bg.paste(self.img_from_DP1, (x << 3, y << 3))
                self.bg.paste(self.img_from_DP2, ((x + 32) << 3, y << 3))
                self.bg.paste(self.img_from_DP1, (x << 3, (y + 30) << 3))
                self.bg.paste(self.img_from_DP2, ((x + 32) << 3, (y + 30) << 3))
        else:
            for x in range(32):
                self.img_from_DP1.putdata(self.get_tile(PPUC1_bit4, x, y, DP1))
                self.img_from_DP2.putdata(self.get_tile(PPUC1_bit4, x, y, DP2))
                self.bg.paste(self.img_from_DP1, (x << 3, y << 3))
                self.bg.paste(self.img_from_DP1, ((x + 32) << 3, y << 3)) 
                self.bg.paste(self.img_from_DP2, (x << 3, (y + 30) << 3))
                self.bg.paste(self.img_from_DP2, ((x + 32) << 3, (y + 30) << 3))

        tmp_bitmap = self.bg.crop((mb.h_scr, mb.v_scr, 255 + mb.h_scr, 239 + mb.v_scr))
        self.bitmap.paste(tmp_bitmap, (0, 0), tmp_bitmap)

    def show_BG(self, mb):
        data_byte = [self.colors[self.BG_PTBL[0]]] * 256 * 240
        self.bitmap.putdata(data_byte)

    # not embedded color pallet yet
    def get_oam_tile(self, mb, plt_num, tile_num):

        tile_num <<= 4
        img = Image.new('RGBA', (8, 8), (0, 0, 0, 0))

        if plt_num == 0:
            color_plt = [(0, 0, 0, 0), self.colors[self.SP_PTBL[1]], self.colors[self.SP_PTBL[2]], self.colors[self.SP_PTBL[3]]]
        else:
            plt_num <<= 2
            color_plt = [(0, 0, 0, 0), self.colors[self.SP_PTBL[plt_num | 1]], self.colors[self.SP_PTBL[plt_num | 2]], self.colors[self.SP_PTBL[plt_num | 3]]]

        if mb.PPUC1 & 0x08:
            for yy in range(8):
                bitmask = 0x80
                for xx in range(8):
                    color = int(self.PTABLE_L[tile_num | yy] & bitmask > 0)
                    color += int(self.PTABLE_L[tile_num | yy | 8] & bitmask > 0) << 1
                    bitmask >>= 1
                    if color:
                        img.putpixel((xx, yy), color_plt[color])
        else:
            for yy in range(8):
                bitmask = 0x80
                for xx in range(8):
                    color = int(self.PTABLE_H[tile_num | yy] & bitmask > 0)
                    color += int(self.PTABLE_H[tile_num | yy | 8] & bitmask > 0) << 1
                    bitmask >>= 1
                    if color:
                        img.putpixel((xx, yy), color_plt[color])
        return img

    def show_OAM_U(self, mb):
        for i in range(64):
            atb = self.SPDATA[(i << 2) | 2]
            if atb & 0x20 > 0:
                continue
            y = self.SPDATA[i << 2]
            if 0xFF >= y >= 0xEF:
                continue
            tile_num = self.SPDATA[(i << 2) | 1]
            x = self.SPDATA[(i << 2) | 3]
            tmp_img = self.get_oam_tile(mb, atb & 0x03, tile_num)

            if atb & 0x80 > 0:
                tmp_img = ImageOps.flip(tmp_img)
            if atb & 0x40 > 0:
                tmp_img = ImageOps.mirror(tmp_img)

            self.bitmap.paste(tmp_img, (x, y - 7), tmp_img)

    def show_OAM_D(self, mb):
        for i in range(64):
            atb = self.SPDATA[(i << 2) | 2]
            if atb & 0x20 == 0:
                continue
            y = self.SPDATA[i << 2]
            if 0xFF >= y >= 0xEF:
                continue
            tile_num = self.SPDATA[(i << 2) | 1]
            x = self.SPDATA[(i << 2) | 3]
            
            tmp_img = self.get_oam_tile(mb, atb & 0x03, tile_num)

            if atb & 0x80:
                tmp_img = ImageOps.flip(tmp_img)
            if atb & 0x40:
                tmp_img = ImageOps.mirror(tmp_img)

            self.bitmap.paste(tmp_img, (x, y - 7), tmp_img)

key = 0
def key_down(e):
    global key
    key = e.keycode  

def show_image(ppu, mb):
    global canvas, item

    root = tkinter.Tk()
    root.title(u'Nes')
    root.geometry("256x240")
    canvas = tkinter.Canvas(master = root, width = 256, height = 240)
    canvas.place(x = 0, y = 0)
    ppu.show_NTBL(mb, 0)
    tk_img = ImageTk.PhotoImage(ppu.bitmap)
    item = canvas.create_image(128, 120, image = tk_img)
    root.bind("<KeyPress>", key_down)

    root.mainloop()

tmp_clk = 0
def main():

    mb  = MotherBoard()
    cpu = CPU()
    ppu = PPU()

    pui = False

    # rom読み込みとリストへの格納
    #f = open('rom//sample1.nes', 'rb')
    #f = open('rom//nestest.nes', 'rb')
    #f = open('rom//MapWalker.nes', 'rb')
    f = open('rom//palette.nes', 'rb')
    #f = open('rom//color_test.nes', 'rb')
    #f = open('rom//test_ppu_read_buffer.nes', 'rb')

    # ROMファイル読み込み
    mb.rom_read(f, ppu)
    # reset irq
    cpu.reset(mb, ppu)

    #  グラフィック表示用のスレッド
    thread1 = threading.Thread(target = show_image, args = (ppu, mb, ))
    thread1.start()

    while True:
        opcode = cpu.fetch(mb, ppu)

        # デバッグ用
        #cpu.debug(mb, ppu)
        #if cpu.PC == 0xC66E:
        #    print('0x01FB:{:#04x}'.format(mb.WRAM[0x01FB]))
        #    print('0x01FC:{:#04x}'.format(mb.WRAM[0x01FC]))
        #    print('0x01FD:{:#04x}'.format(mb.WRAM[0x01FD]))
        #    print('0x01FE:{:#04x}'.format(mb.WRAM[0x01FE]))
        #    print('0x01FF:{:#04x}'.format(mb.WRAM[0x01FF]))
        #    print('0x00D2:{:#04x}'.format(mb.WRAM[0x00D2]))
        #    print('0xC002:{:#04x}'.format(mb.PRGROM2[0x0002]))
        #    print('0xC003:{:#04x}'.format(mb.PRGROM2[0x0003]))
        #    sys.exit()
        tmp_clk = 0

        cpu.execute(opcode, mb, ppu)
        tmp_clk += cpu.clk_table[opcode]
        cpu.cycles += tmp_clk
        ppu.ppu_cycle += (tmp_clk * 3)

        if ppu.ppu_cycle > 341:
            ppu.ppu_cycle -= 341
            cpu.h_line += 1
            
            # v_vlank中のPPUC1bit7の値（0:無効、1:発生）に応じてNMI発生
            if 0 <= cpu.h_line < 240:
                mb.PPUST &= 0x7F

                #  グラフィック表示用の処理
                if cpu.h_line & 0x07 == 7:
                    #t1 = time.perf_counter_ns()
                    ppu.show_BG(mb)
                    ppu.show_OAM_D(mb)
                    ppu.show_NTBL(mb, cpu.h_line)
                    #t2 = time.perf_counter_ns()
                    #print(f"execute:{t2 - t1}")
                    ppu.show_OAM_U(mb)

            elif 240 <= cpu.h_line < 260:
                mb.PPUST |= 0x80
                if mb.PPUC1 & 0x80 > 0 and cpu.h_line == 240:
                    op.nmi(cpu, mb, ppu)

                if cpu.h_line == 240:
                    tk_img = ImageTk.PhotoImage(ppu.bitmap)
                    canvas.itemconfig(item, image = tk_img)

            else:
                cpu.h_line = 0

if __name__ == "__main__":
    main()