# chaigen.py
import operator
import logging


def gen_const(value, to_registry):
    """
    Generates constant of given value.
    Used for generating index of variable to access in memory or constant for assignment operations.
    :param self:
    :param value:
    :param to_registry:
    :return:
    """
    # Clean the to_registry
    code = ['SUB {} {} # BEGIN_CONST_GEN'.format(to_registry, to_registry)]
    code.extend(gen_const_val(value, to_registry))
    return code


def gen_const_val(value, registry):
    """
    Adds given value to target registry.
    :param value: numeric value to add to target registry
    :param registry: registry A-H
    :return:
    """
    code = []

    # # TODO: Replace this with something a bit better!
    # for i in range(value):
    #     code.append('INC {}'.format(registry))

    if value < 10:
        for i in range(value):
            code.append('INC {}'.format(registry))
    else:
        bin_repr = str(bin(value)[2:])

        # print("Binary representation: {}".format(bin_repr))

        size = len(bin_repr)

        for i in range(0, size):
            if bin_repr[i] == '1':
                code.append('INC {}'.format(registry))
            if i < (size - 1):
                code.append('ADD {} {}'.format(registry, registry))

    return code


def gen_arithmetic_operation(operand, pcval):
    """
    Generates code used to perform the arithmetic operations on registers
    -
    Registers are used as follows:
    B - always stores the result of add, sub, mul
    C - second value used in add, sub; first value used in mul
    D - second value used in mul
    -
    :param operand: operator
    :param reg1: registry holding the first value for operation
    :param reg2: registry holding the second value for operation
    :param pcval: value of program counter
    :return:
    """
    if operand == operator.add:
        # regB := regB + regC
        return ['ADD B C']
    elif operand == operator.sub:
        # regB := regB - regC
        return ['SUB B C']
    elif operand == operator.mul:
        # regB := regC * regD
        code = ['SUB B B']  # 1 - Clean B for use later
        start_index = pcval + 2
        end_index = start_index + 8  # 7 - Length of algorithm below
        case_odd_index = start_index + 4  # 6 - 1 - index of
        case_odd_finished_index = start_index + 2

        code.append('JZERO D {} # BEGIN MUL'.format(end_index))  # 2 - while b > 0
        code.append('JODD D {}'.format(case_odd_index))  # 3 - if b is odd jump to 6
        code.append('ADD C C')  # 4 - a = a * 2
        code.append('HALF D')  # 5 - d = d / 2
        code.append('JUMP {}'.format(start_index - 1))  # 6 - goto line 1
        code.append('ADD B C')  # 7 - result += a
        code.append('ADD C C')  # 8
        code.append('HALF D')  # 9
        code.append('JUMP {} # END MUL'.format(start_index - 1))  # 10
        return code
    elif operand == operator.floordiv or operand == operator.mod:
        # Prepare registers for operations (uses all 8 available registers)
        code = []
        start_index = pcval
        if_divisor_zero = start_index + 31
        end_less_condition = start_index + 10
        cond_alt = start_index + 13

        code.append('SUB D D # BEGIN MOD/DIV')  # D - result of division
        code.append('SUB E E')  # E - multiplier
        code.append('INC E')
        code.append('COPY F B')  # F - remainder
        code.append('JZERO C {}'.format(if_divisor_zero))  # if divisor == 0

        code.append('COPY H C')  # WHILE LOOP
        code.append('INC H')
        code.append('SUB H B')
        code.append('JZERO H {}'.format(end_less_condition))  # while divisor < divident
        code.append('JUMP {}'.format(cond_alt))
        code.append('ADD C C')  # divisor * 2
        code.append('ADD E E')  # multiplier * 2
        code.append('JUMP {}'.format(start_index + 5))
        code.append('COPY H C')  # reminder >= divisor
        code.append('SUB H F')
        code.append('JZERO H {}'.format(start_index + 17))
        code.append('JUMP {}'.format(start_index + 19))
        code.append('SUB F C')
        code.append('ADD D E')
        code.append('HALF C')
        code.append('HALF E')
        code.append('JZERO E {}'.format(start_index + 32))
        code.append('COPY H C')
        code.append('SUB H F')
        code.append('JZERO H {}'.format(start_index + 26))
        code.append('JUMP {}'.format(start_index + 28))
        code.append('SUB F C')
        code.append('ADD D E')
        code.append('HALF C')
        code.append('HALF E')
        code.append('JUMP {}'.format(start_index + 21))

        code.append('SUB F F')
        if operand == operator.floordiv:
            code.append('COPY H D # END MOD/DIV')
        elif operator == operator.mod:
            code.append('COPY H F # END MOD/DIV')

        return code


def gen_getval(var_mem_index, to_registry):
    """
    Generates the machine code for getting the desired value from memory
    and storing it in given registry
    :param var_mem_index: memory index for pidentifier
    :param to_registry: A-H
    :return: machine code
    """
    code = []
    code.extend(gen_const(value=var_mem_index, to_registry="A"))
    code.append('LOAD {} # GETVAL'.format(to_registry))

    # H always stores the value of previously loaded variable, so for the convention-sake do it here
    if to_registry != "H":
        code.append('COPY H {}'.format(to_registry))

    return code


def gen_storeval(var_mem_index, from_registry):
    """
    Generates code used for storing the value from registry at a given memory index
    :param var_mem_index:
    :param from_registry:
    :return:
    """
    code = []
    code.extend(gen_const(value=var_mem_index, to_registry='A'))
    code.append('STORE {} # STORE_VAL'.format(from_registry))
    return code


def gen_assign_var_to_const(index, value):
    """
    Generates code used for assigning variable to constant
    :param index: index of the variable to perform assignation
    :param value: value to assign to the variable
    :return:
    """
    code = []
    code.extend(gen_const(value=index, to_registry="A"))
    code.extend(gen_const(value=value, to_registry="H"))
    code.append('STORE H')

    return code


def gen_assign_var_to_var(var1_index, var2_index):
    """
    Generates code used for assigning variable to variable (a := b)
    :param var1_index: index of a in mem
    :param var2_index: index of b in mem
    :return:
    """
    code = []
    code.extend(gen_getval(var_mem_index=var2_index, to_registry="H"))  # Get value of B
    code.extend(gen_const(var1_index, 'A'))  # Store index of a in registry A
    code.append('STORE H')  # Assigns a := b
    return code


def gen_assign_index_to_expr(a_vid, b_vid, a_const, b_const, a_array, a_array_offset,
                             a_array_mem_index, b_array, b_array_offset, b_array_mem_index, operand, pc_val):
    """
    Assigns given memory index to expression
    """
    # Generate constant a and store in first_reg registry
    code = []

    if operand == operator.add or operand == operator.sub:
        result_reg, first_reg, second_reg = 'B', 'B', 'C'
    elif operand == operator.mul:
        result_reg, first_reg, second_reg = 'B', 'C', 'D'
    elif operand == operator.floordiv:
        result_reg, first_reg, second_reg = 'D', 'B', 'C'
    elif operand == operator.mod:
        result_reg, first_reg, second_reg = 'F', 'B', 'C'
    else:
        raise Exception("Unsupported operation {} given".format(operand))

    if a_const:
        # If a is a constant, store value of constant in first_reg
        code.extend(gen_const(value=a_vid, to_registry=first_reg))
    elif a_array:
        logging.debug("a given for operand is an array element")

        # Store the memory address of a in A registry
        code.extend(
            gen_arr_index_from_var(var_mem_index=a_vid, array_mem_index=a_array_mem_index, array_offset=a_array_offset))

        # Load the value to first_reg
        code.append('LOAD {}'.format(first_reg))

    else:
        # If a is variable, load it to first_reg
        code.extend(gen_getval(var_mem_index=a_vid, to_registry=first_reg))

    if b_const:
        # If b is a constant, store value of constant in first_reg
        code.extend(gen_const(value=b_vid, to_registry=second_reg))
    elif b_array:
        logging.debug("b given for operand is an array element")

        # Store the memory address of b in A registry
        code.extend(gen_arr_index_from_var(var_mem_index=b_vid, array_mem_index=b_array_mem_index,
                                           array_offset=b_array_offset))

        # Load the value to second_reg
        code.append('LOAD {}'.format(second_reg))
    else:
        # If b is variable, load it to first_reg
        code.extend(gen_getval(var_mem_index=b_vid, to_registry=second_reg))

    # Perform the arithmetic operation
    pc_val += len(code)

    # logging.debug("Program counter val before operation: {}, len_code: {}".format(pc_val, len(code)))
    code.extend(gen_arithmetic_operation(operand, pc_val))

    return code


def gen_assign_var_to_expr(assign_to_var_index, a_vid, b_vid, a_const, b_const, is_a_arra, a_array_offset,
                           a_array_mem_index, is_b_array, b_array_offset, b_array_mem_index, operand, pc_val):
    """
    Generates code used for assigning variable to result of expression
    (x := a OPERAND b where a - const, b - variable)
    :param is_b_array: BOOL
    :param is_a_arra: BOOL
    :param assign_to_var_index: index of variable to assign to new values in memory
    :param b_vid: index of variable in mem or value of constant
    :param a_vid: index of variable in mem or value of constant
    :param b_const: is b constant
    :param a_const: is a constant
    :param operand: operator
    :param pc_val: value of program counter
    :return:
    """
    # Generate constant a and store in first_reg registry
    code = []

    if operand == operator.floordiv:
        result_reg = 'D'
    elif operand == operator.mod:
        result_reg = 'F'
    else:
        result_reg = 'B'

    code.extend(gen_assign_index_to_expr(a_vid, b_vid, a_const, b_const, is_a_arra, a_array_offset,
                                         a_array_mem_index, is_b_array, b_array_offset, b_array_mem_index, operand,
                                         pc_val))

    # Save result of calculations in variable x
    code.extend(gen_storeval(var_mem_index=assign_to_var_index, from_registry=result_reg))
    return code


def gen_assign_array_var_to_expr(var_mem_index, array_mem_index, array_offset, a_vid, b_vid, a_const, b_const,
                                 a_array, a_array_offset,
                                 a_array_mem_index, b_array, b_array_offset, b_array_mem_index, operand, pc_val):
    """
    Assigns array variable to expression
    array(var) := a OPERAND b
    """
    code = []

    if operand == operator.floordiv:
        result_reg = 'D'
    elif operand == operator.mod:
        result_reg = 'F'
    else:
        result_reg = 'B'

    code.extend(gen_assign_index_to_expr(a_vid, b_vid, a_const, b_const, a_array, a_array_offset,
                                         a_array_mem_index, b_array, b_array_offset, b_array_mem_index, operand,
                                         pc_val))

    # Save results of calculations in array(var)
    # Get array index to which we want to assign the expression
    code.extend(gen_arr_index_from_var(var_mem_index, array_mem_index, array_offset))

    # Store new value in array(var)
    code.append('STORE A')
    return code


def gen_arr_index_from_var(var_mem_index, array_mem_index, array_offset):
    """
    Generates array index from value of variable a.
    Used when assigning arr(var) := sth.
    :return:
    """
    code = []

    logging.debug("Using updated method of calculating array indexes")

    # Get the value from VARIABLE at given memory index
    code.extend(gen_getval(var_mem_index=var_mem_index, to_registry='H'))

    # Calculate almost absolute memory index
    # 1. subtract array offset
    code.extend(gen_const(value=array_offset, to_registry='G'))
    code.append('SUB H G')

    # 2. add array mem index + 1
    code.extend(gen_const(value=array_mem_index+1, to_registry='G'))
    code.append('ADD H G')

    # H now stores memory index which we want to access

    # # Add almost_absolute_memory_index to value of VARIABLE to get absolute_memory_index stored in registry A
    # code.extend(gen_const_val(value=almost_absolute_memory_index, registry='H'))
    code.append('COPY A H')
    # code.append('PUT A')

    return code


def gen_assign_array_var_const(const_value, var_mem_index, array_mem_index, array_offset):
    """
    Used to assign array(var) := const_value.
    - First gets the value of var and uses it as index.
    - Then calculates and stores in A absolute memory index of array(var).
    - Finally, assigns array(var) := const_value.
    :return:
    """
    logging.debug("Assigning to array_var at memory index {} constant := {}".format(var_mem_index, const_value))

    code = []
    # Get the array index from value of var and store it in A
    code.extend(gen_arr_index_from_var(var_mem_index, array_mem_index, array_offset))

    # Now generate the constant
    code.extend(gen_const(value=const_value, to_registry='H'))

    # Finally, store the value of constant at array(var)
    code.append('STORE H')
    return code


def gen_assign_array_var_var(to_var_index, var_mem_index, array_mem_index, array_offset):
    """
    Used to assign array(var) := another_var.
    - First gets the value of var and uses it as index.
    - Then calculates and stores in A absolute memory index of array(var).
    - Finally, assigns array(var) := another_var.
    :type to_var_index: index of another_var
    :return:
    """
    logging.debug("Assigning to array_var at memory index {} value of variable at memory index {}".format(
        var_mem_index, to_var_index))

    code = []
    # Get the array index from value of var and store it in A
    code.extend(gen_arr_index_from_var(var_mem_index, array_mem_index, array_offset))

    # Now get the value of another_var
    code.extend(gen_getval(var_mem_index=to_var_index, to_registry='H'))

    # Store the value of another_var in array(var)
    code.append('STORE H')
    return code


def gen_assign_array_var_array_var(to_array_offset, to_array_mem_index, to_var_vid, from_var_mem_index,
                                   from_array_mem_index,
                                   from_array_offset):
    """
    Used to assign array(var) := another_array(another_var)
    :param to_array_offset:
    :param to_array_mem_index:
    :param to_var_vid:
    :param from_var_mem_index:
    :param from_array_mem_index:
    :param from_array_offset:
    :return:
    """
    logging.debug("Assigning to array_var at memory index {} value of array_var at memory index {}".format(
        to_array_mem_index, from_var_mem_index))

    code = []
    # Get value of the to_var from memory
    code.extend(gen_getval(var_mem_index=to_var_vid, to_registry='A'))

    absolute_mem_index = mem_f

    # In registry A we have the index of var we want to access
    # Increment A, which will hold absolute_mem_index = array_mem_index + array_offset + element_index
    code.extend(gen_const_val(value=to_var_vid + to_array_offset + to_array_mem_index, registry='A'))

    # Now get the value stored at calculated index from memory
    code.append('LOAD H')

    # Now load the absolute memory index of target array(var)
    code.extend(gen_arr_index_from_var(var_mem_index=from_var_mem_index, array_mem_index=from_array_mem_index,
                                       array_offset=from_array_offset))

    code.append('STORE H')


def gen_getarr_element(var_mem_index, array_offset, array_mem_index):
    """
    Generates code for returning element of array at given index
    :param var_mem_index:
    :param array_offset:
    :param array_mem_index:
    :return:
    """
    code = []
    code.extend(gen_const(value=var_mem_index, to_registry='H'))
    code.extend(gen_const(value=array_offset, to_registry='G'))
    code.append('SUB H G')
    code.extend(gen_const(value=array_mem_index + 1, to_registry='G'))
    code.append('ADD H G')
    return code


def gen_getarr_element_to_reg(var_mem_index, array_offset, array_mem_index, to_registry):
    """
    Generates code for returning element of array at given index
    :param var_mem_index:
    :param array_offset:
    :param array_mem_index:
    :return:
    """
    code = []
    # absolute_mem_index = var_mem_index - array_offset + array_mem_index + 1
    # code.extend(gen_getval(var_mem_index=absolute_mem_index, to_registry=to_registry))

    code.extend(gen_const(value=var_mem_index, to_registry=to_registry))
    code.extend(gen_const(value=array_offset, to_registry='G'))
    code.append('SUB {} G'.format(to_registry))
    code.extend(gen_const(value=array_mem_index + 1, to_registry='G'))
    code.append('ADD {} G'.format(to_registry))

    return code


def gen_assign_var_to_array_el(var_index, array_mem_index, element_vid, element_const, array_offset):
    """
    Generates the assembly code assigning variable to contents of array element at given index
    x := array(element_vid)
    :param element_const:
    :param element_vid:
    :param var_index:
    :param array_mem_index:
    :return:
    """
    code = []

    if element_const:
        # If element is a constant, we have a index of array we want to access.
        # Generate a constant, taking into account the array offset
        code.extend(gen_getarr_element(var_mem_index=element_vid, array_offset=array_offset,
                                       array_mem_index=array_mem_index))
    else:
        # If element is a variable, we have to get its' contents from memory first
        code.extend(gen_getval(var_mem_index=element_vid, to_registry='A'))

        # In registry A we have the index of var we want to access
        # Calculate absolute_mem_index = array_mem_index + array_offset + element_index by incrementing H
        code.extend(gen_const_val(value=array_mem_index - array_offset + 1, registry='A'))

        # Now get the value stored at calculated index from memory
        code.append('LOAD H # GEN_ASSIGN_VAR_TO_ARRAY_ELEMENT')

    # Store new value of variable
    code.extend(gen_storeval(var_mem_index=var_index, from_registry='H'))
    return code


def gen_write_const(value):
    """
    Generates code writing the value of constant to stdout
    :param value: of constant
    :return:
    """
    code = []
    # Generate const
    code.extend(gen_const(value, 'H'))
    code.append('PUT H')
    return code


def gen_write_var(var_index):
    """
    Generates code writing the variable to stdout
    :param var_index: index of variable in memory
    :return:
    """
    code = []
    code.extend(gen_const(var_index, 'A'))
    code.append('LOAD H')
    code.append('PUT H')
    return code


def gen_write_array_var(var_index, array_index, array_offset):
    """
    Generates assembly code responsible for writing the array(var) contents to stdout
    :param var_index: index of var in memory
    :param array_index: index of array in memory
    :param array_offset: defined array offset
    :return:
    """
    code = []
    code.extend(gen_getarr_element(var_mem_index=var_index, array_offset=array_offset, array_mem_index=array_index))
    code.append('PUT A')
    return code


def gen_read_to_var(var_index):
    """
    Generates assembly code responsible for reading variable value from stdin
    :param var_index: index of variable in memory
    :return:
    """
    code = []
    code.extend(gen_const(value=var_index, to_registry='A'))
    code.append('GET H')
    code.append('STORE H')
    return code


def gen_read_to_array_var(address_index, array_index, array_offset):
    """
    Generates assembly code responsible for reading array element's value from stdin
    :param address_index: index in memory where array index value is stored
    :param array_index: memory index of array
    :param array_offset: array offset value
    :return:
    """
    code = []
    code.extend(gen_getval(var_mem_index=address_index, to_registry='A'))
    code.extend(gen_const_val(value=array_index - array_offset + 1, registry='A'))
    code.append('GET H')
    code.append('STORE H')


# CONTROL FLOW OPERATIONS
# 1. Conditional statements


def gen_compare(first_reg, compareop, second_reg, pcval, commands_length):
    """
    Generates assembly code responsible for comparing given registers' values
    :param first_reg: first reg
    :param compareop: comparision operator (<, >, <=, >=, =, !=)
    :param second_reg: second reg
    :return:
    """
    code = []

    if compareop == operator.gt or compareop == operator.lt:
        # is a > b -> (is a - b > 0 <-> is a - b < 0)
        # (because we work only with positive numbers)
        # TODO: Make sure all is clear here (run over this code again tommorow)

        offset = 0
        condition_length = 2
        jump_end = pcval + condition_length + commands_length + offset

        code.append('SUB {} {} # BEGIN GT/LT COND'.format(first_reg, second_reg))
        code.append('JZERO {} {} # END GT/LT COND'.format(first_reg, jump_end))

    elif compareop == operator.ge or compareop == operator.le:
        # is a >= b
        offset = 0
        condition_length = 3
        jump_end = pcval + condition_length + commands_length + offset

        code.append('INC {}'.format(first_reg))
        code.append('SUB {} {}'.format(first_reg, second_reg))
        code.append('JZERO {} {}'.format(first_reg, jump_end))

    elif compareop == operator.eq:
        # is a == b
        offset = 0
        condition_length = 6
        jump_to_commands = pcval + condition_length + offset
        jump_end = pcval + condition_length + commands_length + offset

        logging.debug("Jump after commands: {}, jump to commands: {}".format(jump_end, jump_to_commands))

        code.append('INC {}'.format(second_reg))
        code.append('SUB {} {}'.format(second_reg, first_reg))
        code.append('JZERO {} {}'.format(second_reg, jump_end))
        code.append('DEC {}'.format(second_reg))
        code.append('JZERO {} {}'.format(second_reg, jump_to_commands))
        code.append('JUMP {}'.format(jump_end))

    elif compareop == operator.ne:
        # is a != b
        offset = 0
        condition_length = 5
        jump_to_commands = pcval + condition_length + offset
        jump_end = pcval + condition_length + commands_length + offset

        code.append('INC {} # BEGIN NEQ'.format(second_reg))
        code.append('SUB {} {}'.format(second_reg, first_reg))
        code.append('JZERO {} {}'.format(second_reg, jump_to_commands))
        code.append('DEC {}'.format(second_reg))
        code.append('JZERO {} {} # FINISH NEQ COND'.format(second_reg, jump_end))
        # code.append('JUMP {}'.format(jump_to_commands))

    return code


def gen_compare(first_reg, compareop, second_reg, pcval, commands_length):
    """
    Generates assembly code responsible for comparing given registers' values
    :param first_reg: first reg
    :param compareop: comparision operator (<, >, <=, >=, =, !=)
    :param second_reg: second reg
    :return:
    """
    code = []

    if compareop == operator.gt or compareop == operator.lt:
        # is a > b -> (is a - b > 0 <-> is a - b < 0)
        # (because we work only with positive numbers)
        # TODO: Make sure all is clear here (run over this code again tommorow)

        offset = 0
        condition_length = 2
        jump_end = pcval + condition_length + commands_length + offset

        code.append('SUB {} {} # BEGIN GT/LT COND'.format(first_reg, second_reg))
        code.append('JZERO {} {} # END GT/LT COND'.format(first_reg, jump_end))

    elif compareop == operator.ge or compareop == operator.le:
        # is a >= b
        offset = 0
        condition_length = 3
        jump_end = pcval + condition_length + commands_length + offset

        code.append('INC {} # BEGIN GE/LE COND'.format(first_reg))
        code.append('SUB {} {}'.format(first_reg, second_reg))
        code.append('JZERO {} {} # END GE/LE COND'.format(first_reg, jump_end))

    elif compareop == operator.eq:
        # is a == b
        offset = 0
        condition_length = 6
        jump_to_commands = pcval + condition_length + offset
        jump_end = pcval + condition_length + commands_length + offset

        logging.debug("Jump after commands: {}, jump to commands: {}".format(jump_end, jump_to_commands))

        code.append('INC {} # BEGIN EQ COND'.format(second_reg))
        code.append('SUB {} {}'.format(second_reg, first_reg))
        code.append('JZERO {} {}'.format(second_reg, jump_end))
        code.append('DEC {}'.format(second_reg))
        code.append('JZERO {} {}'.format(second_reg, jump_to_commands))
        code.append('JUMP {} # END EQ COND'.format(jump_end))

    elif compareop == operator.ne:
        # is a != b
        offset = 0
        condition_length = 5
        jump_to_commands = pcval + condition_length + offset
        jump_end = pcval + condition_length + commands_length + offset

        code.append('INC {} # BEGIN NEQ COND'.format(second_reg))
        code.append('SUB {} {}'.format(second_reg, first_reg))
        code.append('JZERO {} {}'.format(second_reg, jump_to_commands))
        code.append('DEC {}'.format(second_reg))
        code.append('JZERO {} {} # END NEQ COND'.format(second_reg, jump_end))
        # code.append('JUMP {}'.format(jump_to_commands))

    return code


def gen_prepare_cond_statement(a_vid, b_vid, a_is_const, b_is_const, a_is_arrvar, b_is_arrvar, a_arr_offset,
                               a_arr_mem, b_arr_offset, b_arr_mem, first_reg, second_reg):
    """
    Loads variables from memory necessary to perform given conditional statement
    :return:
    """
    code = []

    if a_is_const:
        code.extend(gen_const(value=a_vid, to_registry=first_reg))
    elif a_is_arrvar:
        code.extend(gen_getarr_element_to_reg(var_mem_index=a_vid, array_offset=a_arr_offset, array_mem_index=a_arr_mem,
                                       to_registry=first_reg))
    else:
        code.extend(gen_getval(var_mem_index=a_vid, to_registry=first_reg))

    if b_is_const:
        code.extend(gen_const(value=b_vid, to_registry=second_reg))
    elif b_is_arrvar:
        code.extend(gen_getarr_element_to_reg(var_mem_index=b_vid, array_offset=b_arr_offset, array_mem_index=b_arr_mem,
                                       to_registry=second_reg))
    else:
        code.extend(gen_getval(var_mem_index=b_vid, to_registry=second_reg))

    return code


def gen_cond_statement(a_vid, b_vid, commands, compareop, pcval, a_is_const=False, b_is_const=False, a_is_arrvar=False,
                       a_arr_mem=None, a_arr_offset=None, b_is_arrvar=False, b_arr_mem=None, b_arr_offset=None):
    """
    Generates assembly code of is statement
    :param a_vid: a value or index in mem
    :param b_vid: b value or index in mem
    :param a_is_const: True/False
    :param b_is_const: True/False
    :param a_is_arrvar: True/False
    :param b_is_arrvar: True/False
    :param compareop: comparision operator (<, >, <=, >=, =, !=)
    :param pcval: value of program counter before code execution
    :param commands: translated contents of conditional statement
    :param b_arr_offset:
    :param b_arr_mem:
    :param a_arr_offset:
    :param a_arr_mem:
    :return:
    """
    code = []
    # TODO: Check if the change from B, C does not affect code performance!
    first_reg, second_reg = 'F', 'G'

    code.extend(gen_prepare_cond_statement(a_vid, b_vid, a_is_const, b_is_const, a_is_arrvar, b_is_arrvar, a_arr_offset,
                                           a_arr_mem, b_arr_offset, b_arr_mem, first_reg, second_reg))

    pcval += len(code)

    logging.debug("Control flow statement handler invoked conditional statements handler with parameters: commands "
                  "length: {}, "
                  "pcval: {}".format(len(commands), pcval))

    code.extend(gen_compare(first_reg=first_reg, second_reg=second_reg, compareop=compareop, pcval=pcval,
                            commands_length=len(commands)))

    return code


def gen_for_loop(iter_mem_index, from_vid, from_is_const, from_is_arrvar, from_arr_mem, from_arr_offset,
                 to_vid, to_is_const, to_is_arrvar, to_arr_mem, to_arr_offset, compareop, commands, pcval):
    """
    Generates assembly code of is statement
    :return:
    """
    code = []
    first_reg, second_reg = 'F', 'G'

    # Set the beginning value of i (iterator)
    if from_is_const:
        code.extend(gen_assign_var_to_const(index=iter_mem_index, value=from_vid))
    elif from_is_arrvar:
        code.extend(gen_assign_var_to_array_el(var_index=iter_mem_index, array_mem_index=from_arr_mem,
                                               element_vid=from_vid,
                                               element_const=True,
                                               array_offset=from_arr_offset))
    else:
        # code.extend(gen_getval(var_mem_index=from_vid, to_registry='H'))
        code.extend(gen_assign_var_to_var(var1_index=iter_mem_index, var2_index=from_vid))

    begin_concheck_jump_pcval = pcval + len(code)

    # Load value of i from memory
    code.extend(gen_getval(var_mem_index=iter_mem_index, to_registry=first_reg))

    # Load value of to_value
    if to_is_const:
        code.extend(gen_const(value=to_vid, to_registry=second_reg))
    elif to_is_arrvar:
        code.extend(gen_getarr_element_to_reg(var_mem_index=to_vid, array_offset=to_arr_offset,
                                              array_mem_index=to_arr_mem, to_registry=second_reg))
    else:
        code.extend(gen_getval(var_mem_index=to_vid, to_registry=second_reg))

    # code.extend(gen_const(value=to_value, to_registry=second_reg))

    # Generate condition check
    pcval += len(code)
    code.extend(gen_compare(first_reg=second_reg, second_reg=first_reg, compareop=compareop, pcval=pcval,
                            commands_length=len(commands)))

    return code, begin_concheck_jump_pcval


def gen_fordownto_loop(iter_mem_index, from_vid, from_is_const, from_is_arrvar, from_arr_mem, from_arr_offset,
                 to_vid, to_is_const, to_is_arrvar, to_arr_mem, to_arr_offset, compareop, commands, pcval):
    """
    Generates assembly code of is statement
    :return:
    """
    code = []
    first_reg, second_reg = 'F', 'G'

    # Set the beginning value of i (iterator)
    if from_is_const:
        code.extend(gen_assign_var_to_const(index=iter_mem_index, value=from_vid))
    elif from_is_arrvar:
        code.extend(gen_assign_var_to_array_el(var_index=iter_mem_index, array_mem_index=from_arr_mem,
                                               element_vid=from_vid,
                                               element_const=True,
                                               array_offset=from_arr_offset))
    else:
        # code.extend(gen_getval(var_mem_index=from_vid, to_registry='H'))
        code.extend(gen_assign_var_to_var(var1_index=iter_mem_index, var2_index=from_vid))

    begin_concheck_jump_pcval = pcval + len(code)

    # Load value of i from memory
    code.extend(gen_getval(var_mem_index=iter_mem_index, to_registry=first_reg))

    # Load value of to_value
    if to_is_const:
        code.extend(gen_const(value=to_vid, to_registry=second_reg))
    elif to_is_arrvar:
        code.extend(gen_getarr_element_to_reg(var_mem_index=to_vid, array_offset=to_arr_offset,
                                              array_mem_index=to_arr_mem, to_registry=second_reg))
    else:
        code.extend(gen_getval(var_mem_index=to_vid, to_registry=second_reg))

    # Generate condition check
    pcval += len(code)
    code.extend(gen_compare(first_reg=first_reg, second_reg=second_reg, compareop=compareop, pcval=pcval,
                            commands_length=len(commands)))

    return code, begin_concheck_jump_pcval
