"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [None] * 256
        self.reg = [0] * 8
        self.FL = [0] * 8
        self.pc = 0
        self.HLT = 0b00000001
        self.instructions_table = {
            0b10000010: self.ldi,
            0b01000111: self.prn,
            0b01000101: self.push,
            0b01000110: self.pop,
            0b01010000: self.call,
            0b01010001: self.ret,
            0b01010100: self.jump,
            0b01010101: self.jump_if_equal,
            0b01010110: self.jump_if_not_equal,
            0b10100000: self.add,
            0b10100010: self.mul,
            0b10100111: self.compare
        }
        self.sp = 0xF4
        self.reg[7] = self.sp
        pass

    def load(self):
        """Load a program into memory."""
        
        address = 0

        if len(sys.argv) < 2:
            print('ERROR - Provide program address to load')
            return
        
        program_filename = sys.argv[1]

        program_text = open(program_filename).read()
        # print('!!!', type(program_text))
        program_lines = program_text.split('\n')
        program = []

        for line in program_lines:
            blocks = line.split()
            if len(blocks) > 0:
                if blocks[0] != '#':
                    inst = blocks[0]
                    program.append(int(inst, 2))
        
        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]

        for instruction in program:
            self.ram[address] = instruction
            address += 1

    def ram_read(self, add):
        return self.ram[add]

    def ram_write(self, add, value):
        self.ram[add] = value
    

    def ldi(self):
        add = self.ram[self.pc + 1]
        value = self.ram[self.pc + 2]
        # print('Load')
        self.reg[add] = value
        self.pc += 3
    
    def prn(self):
        add = self.ram[self.pc + 1]
        value = self.reg[add]
        # print('Print')
        print(value)
        self.pc += 2
    
    def mul(self):
        add1 = self.ram_read(self.pc + 1)
        add2 = self.ram_read(self.pc + 2)
        # print('Multiply')
        self.alu('MUL', add1, add2)
        self.pc += 3

    def add(self):
        add1 = self.ram_read(self.pc + 1)
        add2 = self.ram_read(self.pc + 2)
        # print('Add')
        self.alu('ADD', add1, add2)
        self.pc += 3
    
    def push(self):
        add = self.ram_read(self.pc + 1)
        self.sp -= 1
        # print('Push')
        self.ram[self.sp] = self.reg[add]
        self.pc += 2
    
    def pop(self):
        add = self.ram_read(self.pc + 1)
        # print('Pop')
        self.reg[add] = self.ram[self.sp]
        self.sp += 1
        self.pc += 2
    
    def call(self):
        # print('Call')
        self.sp -= 1
        self.ram[self.sp] = self.pc + 2
        # print('PC stored as', self.ram[self.sp])
        self.pc = self.reg[self.ram[self.pc + 1]]
    
    def jump(self):
        # print('Jump', self.reg[self.ram[self.pc + 1]])
        self.pc = self.reg[self.ram[self.pc + 1]]
    
    def ret(self):
        # print('Return')
        self.pc = self.ram[self.sp]
        self.sp += 1

    def compare(self):
        add1 = self.ram_read(self.pc + 1)
        add2 = self.ram_read(self.pc + 2)
        # print('Compare')
        self.alu('CMP', add1, add2)
        self.pc += 3
    
    def jump_if_equal(self):
        add = self.reg[self.ram[self.pc + 1]]
        # print('Jump if equal', add)
        if self.FL[7]:
            self.pc = add
        else:
            self.pc += 2
    
    def jump_if_not_equal(self):
        add = self.reg[self.ram[self.pc + 1]]
        # print('Jump if not equal', add)
        if self.FL[5] or self.FL[6]:
            self.pc = add
        else:
            self.pc += 2
    
    def AND(self):
        add1 = self.ram_read(self.pc + 1)
        add2 = self.ram_read(self.pc + 2)
        # print('AND')
        self.alu('AND', add1, add2)
        self.pc += 3

    def NOT(self):
        add1 = self.ram_read(self.pc + 1)
        add2 = 0 # dummy value, will not be used
        # print('NOT')
        self.alu('NOT', add1, add2)
        self.pc += 2

    def OR(self):
        add1 = self.ram_read(self.pc + 1)
        add2 = self.ram_read(self.pc + 2)
        # print('OR')
        self.alu('OR', add1, add2)
        self.pc += 3

    def XOR(self):
        add1 = self.ram_read(self.pc + 1)
        add2 = self.ram_read(self.pc + 2)
        # print('XOR')
        self.alu('XOR', add1, add2)
        self.pc += 3

    def SHL(self):
        add1 = self.ram_read(self.pc + 1)
        add2 = self.ram_read(self.pc + 2)
        # print('SHL')
        self.alu('SHL', add1, add2)
        self.pc += 3

    def SHR(self):
        add1 = self.ram_read(self.pc + 1)
        add2 = self.ram_read(self.pc + 2)
        # print('SHR')
        self.alu('SHR', add1, add2)
        self.pc += 3
    
    def ADDI(self):
        add = self.ram_read(self.pc + 1)
        value = self.ram_read(self.pc + 2)
        # print('Add Immediate')
        self.reg[add] = self.reg[add] + value
        self.pc += 3
    
    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "CMP":
            if self.reg[reg_a] == self.reg[reg_b]:
                self.FL[7] = 1
                self.FL[5] = 0
                self.FL[6] = 0
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.FL[6] = 1
                self.FL[5] = 0
                self.FL[7] = 0
            else:
                self.FL[5] = 1
                self.FL[6] = 0
                self.FL[7] = 0
        elif op == 'AND':
            self.reg[reg_a] = self.reg[reg_a] and self.reg[reg_b]
        elif op == 'NOT':
            self.reg[reg_a] = not self.reg[reg_a]
        elif op == 'OR':
            self.reg[reg_a] = self.reg[reg_a] or self.reg[reg_b]
        elif op == 'MOD':
            if self.reg[reg_b] == 0:
                print('0 division error')
                self.running = False
            else:
                self.reg[reg_a] = self.reg[reg_a] % self.reg[reg_b]
        elif op == 'XOR':
            self.reg[reg_a] = self.reg[reg_a] ^ self.reg[reg_b]
        elif op == 'SHL':
            self.reg[reg_a] = self.reg[reg_a] << self.reg[reg_b]
        elif op == 'SHR':
            self.reg[reg_a] = self.reg[reg_a] >> self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        inst = None

        running = True

        while running:
            inst = self.ram[self.pc]

            if inst in self.instructions_table:
                # print('Instruction:', inst)
                self.instructions_table[inst]()
            elif inst == self.HLT:
                running = False
            else:
                self.pc += 1
            
            # print('** PC', self.pc ,'Register', self.reg, 'Stack Pointer', self.sp)
