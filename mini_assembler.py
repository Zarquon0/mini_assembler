from enum import StrEnum

ASSEMBLY_FILE = "assembly.s"
MACHINE_CODE_FILE = "machine_code.b"

class operation(StrEnum):
    ADD = "add"
    ADDI = "addi"
    SLL = "sll"
    SLLI = "slli"
    SRL = "srl"
    SRLI = "srli"
    XOR = "xor"
    ORI = "ori"
    ANDI = "andi"
    MUL = "mul"
    BEQ = "beq"
    BNE = "bne"
    

# match readline[0]:
#     case operation.ADD | operation.SLL | operation.SRL : 
#         # in R
#         Opcode = "0110011"
#         funct7 = "0000000"
#         match readline[0]:
#             case operation.ADD:
#                 funct3 = "000"
#             case operation.SLL:
#         combine


def matcher(readline:tuple[str]):
    Opcode = ""
    funct3 = ""
    funct7 = ""
    immediate = ""
    R_type_flag = False
    I_type_flag = False
    SB_type_flag = False
    MUL_flag = False
    # global Opcode, funct3, funct7, immediate
    match readline[0]:
    #R-type
        case operation.ADD: 
            Opcode = "0110011"
            funct3 = "000"
            funct7 = "0000000"
            R_type_flag = True

        case operation.SLL:
            Opcode = "0110011"
            funct3 = "001"
            funct7 = "0000000"
            R_type_flag = True

        case operation.SRL:
            Opcode = "0110011"
            funct3 = "101"
            funct7 = "0000000"
            R_type_flag = True

        case operation.XOR:
            Opcode = "0110011"
            funct3 = "100"
            funct7 = "0000000"
            R_type_flag = True

    #I-type
        case operation.ADDI:
            Opcode = "0010011"
            funct3 = "000"
            immediate = readline[2][1:] #drop first bit
            I_type_flag = True
        case operation.SLLI:
            Opcode = "0010011"
            funct3 = "001"
            funct7 = "000000"
            immediate = readline[2][1:] #drop first bit
            I_type_flag = True
        case operation.SRLI:
            Opcode = "0010011"
            funct3 = "101"
            funct7 = "000000"
            immediate = readline[2][1:] #drop first bit
            I_type_flag = True
        case operation.ORI:
            Opcode = "0010011"
            funct3 = "110"
            immediate = readline[2][1:] #drop first bit
            I_type_flag = True
        case operation.ANDI:
            Opcode = "0010011"
            funct3 = "111"
            immediate = readline[2][1:] #drop first bit
            I_type_flag = True

        case operation.BEQ:
            Opcode = "1100011"
            funct3 = "000"
            immediate = readline[2][:-1] #drop last bit
            SB_type_flag = True
        case operation.BNE:
            Opcode = "1100011"
            funct3 = "001"
            immediate = readline[2][:-1] #drop last bit
            SB_type_flag = True

        case operation.MUL:
            Opcode = "0110011"
            funct3 = "000"
            MUL_flag = True
    if (R_type_flag):
        return funct7 + readline[3] + readline[2] + funct3 + readline[1] + Opcode
    elif (I_type_flag):
        return immediate + readline[2] + funct3 + readline[1] + Opcode      
    elif (SB_type_flag):
        return immediate[0] + immediate[2:8] + readline[2] + readline[1] + funct3 + immediate[8] + immediate[1] + Opcode
    elif (MUL_flag):
        return "0000001" + readline[3] + readline[2] + funct3 + readline[1] + Opcode

REG_LIST = [
    "zero", "ra", "sp", "gp", "tp", 
    "t0", "t1", "t2", "s0", "s1", 
    "a0", "a1", "a2", "a3", "a4", "a5", "a6", "a7", 
    "s2", "s3", "s4", "s5", "s6", "s7", "s8", "s9", "s10", "s11",
    "t3", "t4", "t5", "t6"
]

def parse_line(line: str) -> tuple[str] | None:
    comment_start = line.find("#")
    if comment_start != -1: line = line[:comment_start]
    components = line.replace(","," ").split()
    if not components: return None
    return tuple(map(component_parse, components))

def component_parse(comp: str) -> str:
    if comp in operation: # it's an operation
        return comp
    elif comp in REG_LIST: # it's a special register name
        idx = REG_LIST.index(comp)
        return binify(int(idx), 5)
    elif comp[0] == 'x' and comp[1:].isnumeric() and int(comp[1:]) >= 0 and int(comp[1:]) <= 31: # it's of the x<num> form
        return binify(int(comp[1:]), 5)
    elif comp.isnumeric() or comp.lstrip('-').isnumeric():
        return binify(int(comp), 13)
    else:
        raise Exception(f"Unrecognized instruction component: {comp}")
    
def binify(to_bin: int, num_length: int):
    naive_bin = bin(to_bin)
    if naive_bin[0] == '-':
        stripped = naive_bin[3:]
        return format((-1*int(stripped, 2)) & ((1 << num_length) - 1), f'0{num_length}b') # CREDIT: travc - https://stackoverflow.com/questions/1604464/twos-complement-in-python
    else:
        stripped = naive_bin[2:]
        return "0"*(num_length - len(stripped)) + stripped

def test_parse_line():
    assert parse_line("add a0, x0, s0") == ("add", "01010", "00000", "01000")
    assert parse_line("   beq \t x0    x0, ,,, 4 # This is a comment") == ("beq", "00000", "00000", "0000000000100")
    assert parse_line(" addi t3, a3, -5") == ("addi", "11100", "01101", "1111111111011")

if __name__ == "__main__":
    new_script = []
    with open(ASSEMBLY_FILE, 'r') as asm_file:
        for line in asm_file:
            parsed_tuple = parse_line(line.strip())
            machine_code_line = matcher(parsed_tuple)
            hex_machine_code_line = hex(int(machine_code_line, 2))[2:]
            new_script.append(machine_code_line)
    with open(MACHINE_CODE_FILE, 'w') as mc_file:
        mc_file.write('\n'.join(new_script))