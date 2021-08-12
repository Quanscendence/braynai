grammar abc;

/* command:
Grammar change: java org.antlr.v4.Tool -Dlanguage=Python3 -visitor .\abc.g4
Corresponding Code update: abc_lang_visitor.py
Execute: python main.py
Ensure: pip install -r vatsas_requirements.txt  # or requirements.txt
Also install  antlr from antlr.org
Link reference: https://tomassetti.me/antlr-mega-tutorial/
*/

/*
parser rules
*/
prog             : statements EOF;
statements       : statement* ;
statement        : expr ;
expr             : expr (MUL|DIV) expr | NUM
                 | expr (ADD|SUB) expr | NUM; # precedence included
// expr             : expr MATH expr | NUM;


/*
lexer rules
*/

/* operators */
ADD     : '+';
MUL     : '*';
SUB     : '-';
DIV     : '/';
POUND   : '#';

MATH    : ADD|SUB|MUL|DIV; // not used currently


/* types */
NUM     : DIGIT+;
WORD    : LETTER+;

COMMENT : POUND ~[\r\n]* -> channel(HIDDEN);
CPP_COMMENT : DIV DIV ~[\r\n]* -> channel(HIDDEN);
NEWLINE : '\r'?'\n'       -> skip;
SPACE   : (' ' | '\t')+   -> skip;



/*
fragments
*/


fragment LETTER : [A-Z];
fragment A:'A'|'a';    fragment B:'B'|'b';    fragment C:'C'|'c';    fragment D:'D'|'d';    fragment E:'E'|'e';
fragment F:'F'|'f';    fragment G:'G'|'g';    fragment H:'H'|'h';    fragment I:'I'|'i';    fragment J:'J'|'j';
fragment K:'K'|'k';    fragment L:'L'|'l';    fragment M:'M'|'m';    fragment N:'N'|'n';    fragment O:'O'|'o';
fragment P:'P'|'p';    fragment Q:'Q'|'q';    fragment R:'R'|'r';    fragment S:'S'|'s';    fragment T:'T'|'t';
fragment U:'U'|'u';    fragment V:'V'|'v';    fragment W:'W'|'w';    fragment X:'X'|'x';    fragment Y:'Y'|'y';
fragment Z:'Z'|'z';
fragment DIGIT : [0-9];
