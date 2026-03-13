addi	a0, x0, 6 # this is n 
addi	t0, x0, 1 # this is fact
addi	a1, x0, 1 # this is i
mul 	t0, t0, a1
addi 	a1, a1, 1
bne 	a1, a0, -8
mul 	t0, t0, a1
beq 	x0, x0, 8
add 	a0, s0, x1