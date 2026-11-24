# Complex-Number-Calculator-Interpreter
Specifications of your project topic

Interpreter for expressions over complex numbers.
Grammar (LL(1), left recursion 

    program    -> expr $$
    expr       -> term expr_tail
    expr_tail  -> add_op term expr_tail | epsilon
    term       -> factor term_tail
    term_tail  -> mult_op factor term_tail | epsilon
    factor     -> '(' factor_body
    factor_body-> expr ')'                      (starts with '(')
                | complex ')'                   (starts with '-' or number)
    complex    -> ['-'] NUMBER add_op NUMBER 'i'
    add_op     -> '+' | '-'
    mult_op    -> '*' | '/'

Because every expression starts with '(', one token of lookahead after
consuming '(' tells us whether we have a grouped expression or a complex
number literal.


Description of the implementation

Challenges encountered

Discussion of the results achieved

An annex with the code you developed. 
