from enum import StrEnum

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
            new_script.append(machine_code_line)
    with open(MACHINE_CODE_FILE, 'w') as mc_file:
        mc_file.write('\n'.join(new_script))