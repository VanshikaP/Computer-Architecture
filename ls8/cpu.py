"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [None] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.LDI = 0b10000010
        self.HLT = 0b00000001
        self.PRN = 0b01000111
        self.MUL = 0b10100010
        self.PUSH = 0b01000101
        self.POP = 0b01000110
        self.instructions_table = {}
        self.instructions_table[self.LDI] = self.ldi
        self.instructions_table[self.PRN] = self.prn
        self.instructions_table[self.MUL] = self.mul
        self.instructions_table[self.PUSH] = self.push
        self.instructions_table[self.POP] = self.pop
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
        self.reg[add] = value
        self.pc += 3
    
    def prn(self):
        add = self.ram[self.pc + 1]
        value = self.reg[add]
        print(value)
        self.pc += 2
    
    def mul(self):
        add1 = self.ram_read(self.pc + 1)
        add2 = self.ram_read(self.pc + 2)
        self.alu('MUL', add1, add2)
        self.pc += 3
    
    def push(self):
        add = self.ram_read(self.pc + 1)
        self.sp -= 1
        self.ram[self.sp] = self.reg[add]
        self.pc += 2
    
    def pop(self):
        add = self.ram_read(self.pc + 1)
        self.reg[add] = self.ram[self.sp]
        self.sp += 1
        self.pc += 2

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
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
