# -*- coding:utf-8 -*-

import ctypes
import opcodes as op
import sys
import tkinter
import threading
from PIL import Image, ImageTk

# キャンバスのサイズ設定
CANVAS_WIDTH = 256
CANVAS_HEIGHT = 240

# キー入力判定
def isPressed(key):
    return (bool(ctypes.windll.user32.GetAsyncKeyState(key) & 0x8000))

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
        self.PC = 0xC000

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
        if opcode == 0xA5:
            op.lda_im8(self, mb, ppu)
        if opcode == 0xB5:
            op.lda_im8x(self, mb, ppu)
        if opcode == 0xAD:
            op.lda_im16(self, mb, ppu)
        if opcode == 0xBD:
            op.lda_im16x(self, mb, ppu)
        if opcode == 0xB9:
            op.lda_im16y(self, mb, ppu)
        if opcode == 0xA1:
            op.lda_iim8x(self, mb, ppu)
        if opcode == 0xB1:
            op.lda_iim8y(self, mb, ppu)
        # LDX命令
        if opcode == 0xA2:
            op.ldx_sim8(self, mb, ppu)
        if opcode == 0xA6:
            op.ldx_im8(self, mb, ppu)
        if opcode == 0xB6:
            op.ldx_im8y(self, mb, ppu)
        if opcode == 0xAE:
            op.ldx_im16(self, mb, ppu)
        if opcode == 0xBE:
            op.ldx_im16y(self, mb, ppu)
        # LDY命令
        if opcode == 0xA0:
            op.ldy_sim8(self, mb, ppu)
        if opcode == 0xA4:
            op.ldy_im8(self, mb, ppu)
        if opcode == 0xB4:
            op.ldy_im8x(self, mb, ppu)
        if opcode == 0xAC:
            op.ldy_im16(self, mb, ppu)
        if opcode == 0xBC:
            op.ldy_im16x(self, mb, ppu)
        # STA命令
        if opcode == 0x85:
            op.sta_im8(self, mb, ppu) 
        if opcode == 0x95:
            op.sta_im8x(self, mb, ppu) 
        if opcode == 0x8D:
            op.sta_im16(self, mb, ppu)
        if opcode == 0x9D:
            op.sta_im16x(self, mb, ppu)
        if opcode == 0x99:
            op.sta_im16y(self, mb, ppu) 
        if opcode == 0x81:
            op.sta_iim8x(self, mb, ppu)
        if opcode == 0x91:
            op.sta_iim8y(self, mb, ppu)
        # STX命令
        if opcode == 0x86:
            op.stx_im8(self, mb, ppu)
        if opcode == 0x96:
            op.stx_im8y(self, mb, ppu)
        if opcode == 0x8E:
            op.stx_im16(self, mb, ppu)
        # STY命令
        if opcode == 0x84:
            op.sty_im8(self, mb, ppu)
        if opcode == 0x94:
            op.sty_im8x(self, mb, ppu)
        if opcode == 0x8C:
            op.sty_im16(self, mb, ppu)
        # TAX命令
        if opcode == 0xAA:
            op.tax(self, mb)
        # TAY命令
        if opcode == 0xA8:
            op.tay(self, mb)
        # TSX命令
        if opcode == 0xBA:
            op.tsx(self, mb)
        # TXA命令
        if opcode == 0x8A:
            op.txa(self, mb)
        # TXS命令
        if opcode == 0x9A:
            op.txs(self, mb)
        # TYA命令
        if opcode == 0x98:
            op.tya(self, mb)
        # 算術命令
        # ADC命令
        if opcode == 0x69:
            op.adc_sim8(self, mb, ppu)
        if opcode == 0x65:
            op.adc_im8(self, mb, ppu)
        if opcode == 0x75:
            op.adc_im8x(self, mb, ppu)
        if opcode == 0x6D:
            op.adc_im16(self, mb, ppu)
        if opcode == 0x7D:
            op.adc_im16x(self, mb, ppu)
        if opcode == 0x79:
            op.adc_im16y(self, mb, ppu)
        if opcode == 0x61:
            op.adc_iim8x(self, mb, ppu)
        if opcode == 0x71:
            op.adc_iim8y(self, mb, ppu)
        # AND命令
        if opcode == 0x29:
            op.and_sim8(self, mb, ppu)
        if opcode == 0x25:
            op.and_im8(self, mb, ppu)
        if opcode == 0x35:
            op.and_im8x(self, mb, ppu)
        if opcode == 0x2D:
            op.and_im16(self, mb, ppu)
        if opcode == 0x3D:
            op.and_im16x(self, mb, ppu)
        if opcode == 0x39:
            op.and_im16y(self, mb, ppu)
        if opcode == 0x21:
            op.and_iim8x(self, mb, ppu)
        if opcode == 0x31:
            op.and_iim8y(self, mb, ppu)
        # ASL命令
        if opcode == 0x0A:
            op.asl_acc(self, mb)
        if opcode == 0x06:
            op.asl_im8(self, mb, ppu)
        if opcode == 0x16:
            op.asl_im8x(self, mb, ppu)
        if opcode == 0x0E:
            op.asl_im16(self, mb, ppu)
        if opcode == 0x1E:
            op.asl_im16x(self, mb, ppu)
        # BIT命令
        if opcode == 0x24:
            op.bit_im8(self, mb, ppu)
        if opcode == 0x2C:
            op.bit_im16(self, mb, ppu)           
        # CMP命令
        if opcode == 0xC9:
            op.cmp_sim8(self, mb, ppu)
        if opcode == 0xC5:
            op.cmp_im8(self, mb, ppu)
        if opcode == 0xD5:
            op.cmp_im8x(self, mb, ppu)
        if opcode == 0xCD:
            op.cmp_im16(self, mb, ppu)
        if opcode == 0xDD:
            op.cmp_im16x(self, mb, ppu)
        if opcode == 0xD9:
            op.cmp_im16y(self, mb, ppu)
        if opcode == 0xC1:
            op.cmp_iim8x(self, mb, ppu)
        if opcode == 0xD1:
            op.cmp_iim8y(self, mb, ppu)
        # CPX命令
        if opcode == 0xE0:
            op.cpx_sim8(self, mb, ppu)
        if opcode == 0xE4:
            op.cpx_im8(self, mb, ppu)
        if opcode == 0xEC:
            op.cpx_im16(self, mb, ppu)
        # CPY命令
        if opcode == 0xC0:
            op.cpy_sim8(self, mb, ppu)
        if opcode == 0xC4:
            op.cpy_im8(self, mb, ppu)
        if opcode == 0xCC:
            op.cpy_im16(self, mb, ppu)
        # DEC命令
        if opcode == 0xC6:
            op.dec_im8(self, mb, ppu)
        if opcode == 0xD6:
            op.dec_im8x(self, mb, ppu)
        if opcode == 0xCE:
            op.dec_im16(self, mb, ppu)
        if opcode == 0xDE:
            op.dec_im16x(self, mb, ppu)
        # DEX命令
        if opcode == 0xCA:
            op.dex(self, mb) 
        # DEY命令
        if opcode == 0x88:
            op.dey(self, mb) 
        # EOR命令
        if opcode == 0x49:
            op.eor_sim8(self, mb, ppu)
        if opcode == 0x45:
            op.eor_im8(self, mb, ppu)
        if opcode == 0x55:
            op.eor_im8x(self, mb, ppu)
        if opcode == 0x4D:
            op.eor_im16(self, mb, ppu)
        if opcode == 0x5D:
            op.eor_im16x(self, mb, ppu)
        if opcode == 0x59:
            op.eor_im16y(self, mb, ppu)
        if opcode == 0x41:
            op.eor_iim8x(self, mb, ppu)
        if opcode == 0x51:
            op.eor_iim8y(self, mb, ppu)
        # INC命令
        if opcode == 0xE6:
            op.inc_im8(self, mb, ppu)
        if opcode == 0xF6:
            op.inc_im8x(self, mb, ppu)
        if opcode == 0xEE:
            op.inc_im16(self, mb, ppu)
        if opcode == 0xFE:
            op.inc_im16x(self, mb, ppu)
        # INX命令
        if opcode == 0xE8:
            op.inx(self, mb)
        # INY命令
        if opcode == 0xC8:
            op.iny(self, mb)
        # LSR命令
        if opcode == 0x4A:
            op.lsr_acc(self, mb)
        if opcode == 0x46:
            op.lsr_im8(self, mb, ppu)
        if opcode == 0x56:
            op.lsr_im8x(self, mb, ppu)
        if opcode == 0x4E:
            op.lsr_im16(self, mb, ppu)
        if opcode == 0x5E:
            op.lsr_im16x(self, mb, ppu)
        # ORA命令
        if opcode == 0x09:
            op.ora_sim8(self, mb, ppu)
        if opcode == 0x05:
            op.ora_im8(self, mb, ppu)
        if opcode == 0x15:
            op.ora_im8x(self, mb, ppu)
        if opcode == 0x0D:
            op.ora_im16(self, mb, ppu)
        if opcode == 0x1D:
            op.ora_im16x(self, mb, ppu)
        if opcode == 0x19:
            op.ora_im16y(self, mb, ppu)
        if opcode == 0x01:
            op.ora_iim8x(self, mb, ppu)
        if opcode == 0x11:
            op.ora_iim8y(self, mb, ppu)
        # ROL命令
        if opcode == 0x2A:
            op.rol_acc(self, mb)
        if opcode == 0x26:
            op.rol_im8(self, mb, ppu)
        if opcode == 0x36:
            op.rol_im8x(self, mb, ppu)
        if opcode == 0x2E:
            op.rol_im16(self, mb, ppu)
        if opcode == 0x3E:
            op.rol_im16x(self, mb, ppu)
        # ROR命令
        if opcode == 0x6A:
            op.ror_acc(self, mb)
        if opcode == 0x66:
            op.ror_im8(self, mb, ppu)
        if opcode == 0x76:
            op.ror_im8x(self, mb, ppu)
        if opcode == 0x6E:
            op.ror_im16(self, mb, ppu)
        if opcode == 0x7E:
            op.ror_im16x(self, mb, ppu)
        # SBC命令
        if opcode == 0xE9:
            op.sbc_sim8(self, mb, ppu)
        if opcode == 0xE5:
            op.sbc_im8(self, mb, ppu)
        if opcode == 0xF5:
            op.sbc_im8x(self, mb, ppu)
        if opcode == 0xED:
            op.sbc_im16(self, mb, ppu)
        if opcode == 0xFD:
            op.sbc_im16x(self, mb, ppu)
        if opcode == 0xF9:
            op.sbc_im16y(self, mb, ppu)
        if opcode == 0xE1:
            op.sbc_iim8x(self, mb, ppu)
        if opcode == 0xF1:
            op.sbc_iim8y(self, mb, ppu)
        # スタック命令
        # PHA命令
        if opcode == 0x48:
            op.pha(self, mb, ppu)
        # PHP命令
        if opcode == 0x08:
            op.php(self, mb, ppu)
        # PLA命令
        if opcode == 0x68:
            op.pla(self, mb, ppu)
        # PLP命令
        if opcode == 0x28:
            op.plp(self, mb, ppu)
        # ジャンプ命令
        # JMP命令
        if opcode == 0x4C:
            op.jmp_im16(self, mb, ppu)
        if opcode == 0x6C:
            op.jmp_iim8(self, mb, ppu)
        # JSR命令
        if opcode == 0x20:
            op.jsr(self, mb, ppu)
        # RTS命令
        if opcode == 0x60:
            op.rts(self, mb, ppu)
        # RTI命令
        if opcode == 0x40:
            op.rti(self, mb, ppu)
        # 分岐命令
        # BCC命令
        if opcode == 0x90:
            op.bcc(self, mb, ppu)
        # BCS命令
        if opcode == 0xB0:
            op.bcs(self, mb, ppu)
        # BEQ命令
        if opcode == 0xF0:
            op.beq(self, mb, ppu)
        # BMI命令
        if opcode == 0x30:
            op.bmi(self, mb, ppu)
        # BNE命令
        if opcode == 0xD0:
            op.bne(self, mb, ppu)
        # BPL命令
        if opcode == 0x10:
            op.bpl(self, mb, ppu)
        # BVC命令
        if opcode == 0x50:
            op.bvc(self, mb, ppu)
        # BVS命令
        if opcode == 0x70:
            op.bvs(self, mb, ppu)
        # フラグ変更命令
        # CLC命令
        if opcode == 0x18:
            op.clc(self, mb)
        # CLD命令　BCDモードからの復帰らしい
        if opcode == 0xD8:
            op.cld(self, mb)
        # CLI命令
        if opcode == 0x58:
            op.cli(self, mb)
        # CLV命令
        if opcode == 0xB8:
            op.clv(self, mb)
        # SEC命令
        if opcode == 0x38:
            op.sec(self, mb)
        # SED命令
        if opcode == 0xF8:
            op.sed(self, mb)
        # SEI命令
        if opcode == 0x78:
            op.sei(self, mb)
        # その他の命令
        # BRK命令
        if opcode == 0x00:
            op.brk(self, mb, ppu)
        # NOP命令
        if opcode == 0xEA:
            op.nop(self, mb)
        if opcode == 0x04:
            op.undef_nop1(self, mb)
        if opcode == 0x44:
            op.undef_nop1(self, mb)
        if opcode == 0x64:
            op.undef_nop1(self, mb)
        if opcode == 0x0C:
            op.undef_nop2(self, mb)
        if opcode == 0x14:
            op.undef_nop1(self, mb)
        if opcode == 0x34:
            op.undef_nop1(self, mb)
        if opcode == 0x54:
            op.undef_nop1(self, mb)
        if opcode == 0x74:
            op.undef_nop1(self, mb)
        if opcode == 0xD4:
            op.undef_nop1(self, mb)
        if opcode == 0xF4:
            op.undef_nop1(self, mb)
        if opcode == 0x1A:
            op.nop(self, mb)
        if opcode == 0x3A:
            op.nop(self, mb)
        if opcode == 0x5A:
            op.nop(self, mb)
        if opcode == 0x7A:
            op.nop(self, mb)
        if opcode == 0xDA:
            op.nop(self, mb)
        if opcode == 0xFA:
            op.nop(self, mb)
        if opcode == 0x80:
            op.undef_nop1(self, mb)
        if opcode == 0x1C:
            op.undef_nop2(self, mb)
        if opcode == 0x3C:
            op.undef_nop2(self, mb)
        if opcode == 0x5C:
            op.undef_nop2(self, mb)
        if opcode == 0x7C:
            op.undef_nop2(self, mb)
        if opcode == 0xDC:
            op.undef_nop2(self, mb)
        if opcode == 0xFC:
            op.undef_nop2(self, mb)

class MotherBoard:
    def __init__(self):
        self.WRAM    = [0x00] * 0x0800 # $0000～$07FF
        self.EXROM1  = [0x00] * 0x1FE0 # $4020～$5FFF
        self.EXROM2  = [0x00] * 0x2000 # $6000～$7FFF
        self.PRGROM1 = [0x00] * 0x4000 # $8000～$BFFF
        self.PRGROM2 = [0x00] * 0x4000 # $C000～$FFFF

        self.PPUC1 = 0x00 # PPU制御レジスタ１@0x2000
        self.PPUC2 = 0x00 # PPU制御レジスタ２@0x2001
        self.PPUST = 0x00 # PPUステータスレジスタ@0x2002
        self.OAMAD = 0x00 # 書き込むsprite領域のアドレス @0x2003
        self.OAMDATA = 0x00 # sprite領域のデータ @0x2004
        self.PPUSCR = 0x00 # 背景スクロール値 @0x2005
        self.VRAMAD = 0x0000 # 書き込むPPUメモリ領域のアドレス@0x2006
        self.F_VRAMAD = True # True:上位アドレス　False:下位アドレス
        self.VRAMAC = 0x00 # PPUメモリ領域のデータ@0x2007

        self.JOYPAD1 = 0x00 # @0x4016
        self.JOYPAD2 = 0x00 # @0x4017

        self.joypad_cnt = 0

        self.WRAM[0xD2] = 0x13

    def joypad(self):
        if self.joypad_cnt == 1:
            if isPressed(65): # a
                return self.JOYPAD1 | 0x01
            else:
                return self.JOYPAD1 & 0xFE
        elif self.joypad_cnt == 2: # s
            if isPressed(83):
                return self.JOYPAD1 | 0x01
            else:
                return self.JOYPAD1 & 0xFE
        elif self.joypad_cnt == 3: # w
            if isPressed(87):
                return self.JOYPAD1 | 0x01
            else:
                return self.JOYPAD1 & 0xFE
        elif self.joypad_cnt == 4: # q
            if isPressed(81):
                return self.JOYPAD1 | 0x01
            else:
                return self.JOYPAD1 & 0xFE
        elif self.joypad_cnt == 5: # up
            if isPressed(38):
                return self.JOYPAD1 | 0x01
            else:
                return self.JOYPAD1 & 0xFE
        elif self.joypad_cnt == 6:
            if isPressed(40): # down
                return self.JOYPAD1 | 0x01
            else:
                return self.JOYPAD1 & 0xFE
        elif self.joypad_cnt == 7:
            if isPressed(37): # left
                return self.JOYPAD1 | 0x01
            else:
                return self.JOYPAD1 & 0xFE
        elif self.joypad_cnt == 8:
            if isPressed(39): # right
                return self.JOYPAD1 | 0x01
            else:
                return self.JOYPAD1 & 0xFE
        else:
            return self.JOYPAD1 & 0xFE

    def show_ppu_reg(self):
        print("0x2006:" + str(self.VRAMAD))

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
            print("not yet!")
            sys.exit()

        if nes_header[5] == 1:
            for i in range(0x1000):
                ppu.PTABLE_H[i] = int.from_bytes(f.read(1), byteorder = sys.byteorder)
        else:
            print("not yet!")
            sys.exit()

        #character_rom_pages = nes_header[5]
        #character_rom_start = 0x0010 + nes_header[4] * 0x4000
        #character_rom_end   = character_rom_start + nes_header[5] * 0x2000

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
        elif addr == 0x2002:
            tmp_PPUST = self.PPUST
            self.PPUST &= 0x7F
            return tmp_PPUST
        elif addr == 0x2004:
            return self.OAMDATA
        elif addr == 0x2007:
            return ppu.read(self.VRAMAD, ppu)
            if self.PPUC1 & 0x04 > 0:
                self.VRAMAD += 32
            else:
                self.VRAMAD += 1
        # PPU I/O mirror
        elif 0x2008 <= addr <= 0x3FFF:
            if addr & 0x0007 == 0x0002:
                tmp_PPUST = self.PPUST
                self.PPUST &= 0x7F
                return tmp_PPUST
            elif addr & 0x0007 == 0x0004:
                return self.OAMDATA
            elif addr & 0x0007 == 0x0007:
                return ppu.read(self.VRAMAD, ppu)
                if self.PPUC1 & 0x04 > 0:
                    self.VRAMAD += 32
                else:
                    self.VRAMAD += 1
        # APU I/O PAD
        elif 0x4000 <= addr <= 0x401F:
            if addr == 0x4016:
                self.joypad_cnt += 1
                return self.joypad()
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
        elif addr == 0x2000:
            self.PPUC1 = data
        elif addr == 0x2001:
            self.PPUC2 = data
        elif addr == 0x2003:
            self.OAMAD = data
        elif addr == 0x2004:
            self.OAMDATA = data
        elif addr == 0x2005:
            self.PPUSCR = data
        elif addr == 0x2006: # 書き込み毎の処理については単純なフラグ反転ではなさそう
            if self.F_VRAMAD == True:
                self.VRAMAD &= 0x00FF
                self.VRAMAD |= (data << 8)
                self.F_VRAMAD = False
            else:
                self.VRAMAD &= 0xFF00
                self.VRAMAD |= data
                self.F_VRAMAD = True
        elif addr == 0x2007:
            ppu.write(self.VRAMAD, data)
            if self.PPUC1 & 0x04 > 0:
                self.VRAMAD += 32
            else:
                self.VRAMAD += 1
        # PPU I/O mirror
        elif 0x2008 <= addr <= 0x3FFF:
            if addr & 0x0007 == 0x0000:
                self.PPUC1 = data
            elif addr & 0x0007 == 0x0001:
                self.PPUC2 = data
            elif addr & 0x0007 == 0x0003:
                self.OAMAD = data
            elif addr & 0x0007 == 0x0004:
                self.OAMDATA = data
            elif addr & 0x0007 == 0x0005:
                self.PPUSCR = data
            elif addr & 0x0007 == 0x0006:
                if self.F_VRAMAD == True:
                    self.VRAMAD &= 0x00FF
                    self.VRAMAD |= (data << 8)
                    self.F_VRAMAD = False
                else:
                    self.VRAMAD &= 0xFF00
                    self.VRAMAD |= data
                    self.F_VRAMAD = True
            elif addr & 0x0007 == 0x0007:
                ppu.write(self.VRAMAD, data)
                if self.PPUC1 & 0x04 > 0:
                    self.VRAMAD += 32
                else:
                    self.VRAMAD += 1
        # APU I/O PAD
        elif 0x4000 <= addr <= 0x401F:
            if addr == 0x4016:
                self.JOYPAD1 = data
                if data & 0x01 == 1:
                    self.joypad_cnt = 0
            if addr == 0x4017:
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

        self.bitmap = Image.new('RGB', (256, 240), (0, 0, 0))

        self.ppu_cycle = 0x00

    def write(self, addr, data):
        if 0x0000 <= addr <= 0x0FFF:
            self.PTABLE_H[addr - 0x0000] = data
        elif 0x1000 <= addr <= 0x1FFF:
            self.PTABLE_L[addr - 0x1000] = data

        elif 0x2000 <= addr <= 0x23BF:
            self.DP1_NTBL[addr - 0x2000] = data
        elif 0x23C0 <= addr <= 0x23FF:
            self.DP1_ATBL[addr - 0x23C0] = data

        elif 0x2400 <= addr <= 0x27BF:
            self.DP2_NTBL[addr - 0x2400] = data
        elif 0x27C0 <= addr <= 0x27FF:
            self.DP2_ATBL[addr - 0x27C0] = data

        elif 0x2800 <= addr <= 0x2BBF:
            self.DP1_NTBL[addr - 0x2800] = data
        elif 0x2BC0 <= addr <= 0x2BFF:
            self.DP1_ATBL[addr - 0x2BC0] = data

        elif 0x2C00 <= addr <= 0x2FBF:
            self.DP2_NTBL[addr - 0x2C00] = data
        elif 0x2FC0 <= addr <= 0x2FFF:
            self.DP2_ATBL[addr - 0x2FC0] = data

        elif 0x3F00 <= addr <= 0x3F0F:
            self.BG_PTBL[addr - 0x3F00]  = data
        elif 0x3F10 <= addr <= 0x3F1F:
            self.SP_PTBL[addr - 0x3F10]  = data

    def read(self, addr):
        if 0x0000 <= addr <= 0x0FFF:
            return self.PTABLE_H[addr - 0x0000]
        elif 0x1000 <= addr <= 0x1FFF:
            return self.PTABLE_L[addr - 0x1000]

        elif 0x2000 <= addr <= 0x23BF:
            return self.DP1_NTBL[addr - 0x2000]
        elif 0x23C0 <= addr <= 0x23FF:
            return self.DP1_ATBL[addr - 0x23C0]

        elif 0x2400 <= addr <= 0x27BF:
            return self.DP2_NTBL[addr - 0x2400]
        elif 0x27C0 <= addr <= 0x27FF:
            return self.DP2_ATBL[addr - 0x27C0]

        elif 0x2800 <= addr <= 0x2BBF:
            return self.DP1_NTBL[addr - 0x2800]
        elif 0x2BC0 <= addr <= 0x2BFF:
            return self.DP1_ATBL[addr - 0x2BC0]

        elif 0x2C00 <= addr <= 0x2FBF:
            return self.DP2_NTBL[addr - 0x2C00]
        elif 0x2FC0 <= addr <= 0x2FFF:
            return self.DP2_ATBL[addr - 0x2FC0]

        elif 0x3F00 <= addr <= 0x3F0F:
            return self.BG_PTBL[addr - 0x3F00]
        elif 0x3F10 <= addr <= 0x3F1F:
            return self.SP_PTBL[addr - 0x3F10]

    # not embedded color pallet yet
    def tile_2_splt(self, mb, splt_num):
        img = Image.new('RGB', (8, 8), (0, 0, 0))
        for y in range(0x08):
            bitmask = 0x80
            for x in range(8):
                color = self.PTABLE_H[splt_num * 0x10 + y] & bitmask
                color += (self.PTABLE_H[splt_num * 0x10 + y + 8] & bitmask) << 1
                bitmask >>= 1
                if color == 0:
                    img.putpixel((x, y), (220, 220, 220))
                if color == 1:
                    img.putpixel((x, y), (128, 128, 128))
                if color == 2:
                    img.putpixel((x, y), (64, 64, 64))
                if color == 3:
                    img.putpixel((x, y), (0, 0, 0))

        return img

    def show_DP1_NTBL(self, mb):
        for x in range(32):
            for y in range(30):
                splt_num = self.DP1_NTBL[x + (y << 5)]
                self.bitmap.paste(self.tile_2_splt(mb, splt_num), (x << 3, y << 3))

        return self.bitmap

    def show(self):
        print(self.DP1_NTBL)

def show_image(ppu, mb):
    global canvas, item

    root = tkinter.Tk()
    root.title(u'Nes')
    root.geometry("256x240")
    canvas = tkinter.Canvas(master = root, width = 256, height = 240)
    canvas.place(x = 0, y = 0)
    img = ppu.show_DP1_NTBL(mb)
    tk_img = ImageTk.PhotoImage(img)
    item = canvas.create_image(128, 120, image = tk_img)

    root.mainloop()

def main():
    mb  = MotherBoard()
    cpu = CPU()
    ppu = PPU()

    pui = False

    # rom読み込みとリストへの格納
    #f = open('rom//sample1.nes', 'rb')
    f = open('rom//nestest.nes', 'rb')

    # ROMファイル読み込み
    mb.rom_read(f, ppu)
    # reset irq
    cpu.reset(mb, ppu)

    #  グラフィック表示用のスレッド
    #thread1 = threading.Thread(target = show_image, args = (ppu, mb, ))
    #thread1.start()

    for _ in range(0x100000):
        opcode = cpu.fetch(mb, ppu)

        # デバッグ用
        #print(format(opcode, '#04x'))
        cpu.debug(mb, ppu)
#
        if cpu.PC == 0xc66E:
        
            print('0x01FB:{:#04x}'.format(mb.WRAM[0x01FB]))
            print('0x01FC:{:#04x}'.format(mb.WRAM[0x01FC]))
            print('0x01FD:{:#04x}'.format(mb.WRAM[0x01FD]))
            print('0x01FE:{:#04x}'.format(mb.WRAM[0x01FE]))
            print('0x01FF:{:#04x}'.format(mb.WRAM[0x01FF]))
            print('0x00D2:{:#04x}'.format(mb.WRAM[0x00D2]))
            print('0xC002:{:#04x}'.format(mb.PRGROM2[0x0002]))
            print('0xC003:{:#04x}'.format(mb.PRGROM2[0x0003]))
            sys.exit()

        #print(cpu.h_line)
        #mb.show_ppu_reg() <= 使わない

        cpu.execute(opcode, mb, ppu)
        cpu.cycles += cpu.clk_table[opcode]
        ppu.ppu_cycle += (cpu.clk_table[opcode] * 3)
        
        if ppu.ppu_cycle > 341:
            ppu.ppu_cycle -= 341
            cpu.h_line += 1
            
            # v_vlank中のPPUC1bit7の値（0:無効、1:発生）に応じてNMI発生
            if 0 <= cpu.h_line < 240:
                mb.PPUST &= 0x7F
            elif 240 <= cpu.h_line < 260:
                mb.PPUST |= 0x80
                if mb.PPUC1 & 0x80 > 0:
                    op.nmi(cpu, mb, ppu)
            else:
                cpu.h_line = 0

            #  グラフィック表示用の処理
            #if cpu.h_line % 8 == 0:
            #    img = ppu.show_DP1_NTBL(mb)
            #    tk_img = ImageTk.PhotoImage(img)
            #    canvas.itemconfig(item, image = tk_img)

        #img = ppu.show_DP1_NTBL(mb)

    #ppu.show()
    
    #ppu.sprite_2_8x8(mb, 0x62)
    

if __name__ == "__main__":
    main()