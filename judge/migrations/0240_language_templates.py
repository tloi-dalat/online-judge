from django.db import migrations

TEMPLATES = {
    'PY2': (
        'import sys\n'
        '\n'
        'input = sys.stdin.readline\n'
        '\n'
        '\n'
        'def main():\n'
        '    pass\n'
        '\n'
        '\n'
        "if __name__ == '__main__':\n"
        '    main()\n'
    ),
    'PY3': (
        'import sys\n'
        '\n'
        'input = sys.stdin.readline\n'
        '\n'
        '\n'
        'def main():\n'
        '    pass\n'
        '\n'
        '\n'
        "if __name__ == '__main__':\n"
        '    main()\n'
    ),
    'PYPY': (
        'import sys\n'
        '\n'
        'input = sys.stdin.readline\n'
        '\n'
        '\n'
        'def main():\n'
        '    pass\n'
        '\n'
        '\n'
        "if __name__ == '__main__':\n"
        '    main()\n'
    ),
    'PYPY3': (
        'import sys\n'
        '\n'
        'input = sys.stdin.readline\n'
        '\n'
        '\n'
        'def main():\n'
        '    pass\n'
        '\n'
        '\n'
        "if __name__ == '__main__':\n"
        '    main()\n'
    ),
    'PAS': (
        'program main;\n'
        '\n'
        'begin\n'
        '\n'
        'end.\n'
    ),
    'PERL': (
        'use strict;\n'
        'use warnings;\n'
        '\n'
    ),
    'LUA': (
        'local function main()\n'
        '\n'
        'end\n'
        '\n'
        'main()\n'
    ),
    'KOTLIN': (
        'import java.io.*\n'
        'import java.util.*\n'
        '\n'
        'fun main() {\n'
        '\n'
        '}\n'
    ),
    'RUBY18': (
        'def main\n'
        'end\n'
        '\n'
        'main\n'
    ),
    'RUBY': (
        'def main\n'
        'end\n'
        '\n'
        'main\n'
    ),
    'PHP': (
        '<?php\n'
        '\n'
    ),
    'MONOCS': (
        'using System;\n'
        'using System.Collections.Generic;\n'
        'using System.Linq;\n'
        '\n'
        'class Program {\n'
        '    static void Main() {\n'
        '\n'
        '    }\n'
        '}\n'
    ),
    'HASK': (
        'main :: IO ()\n'
        'main = do\n'
        '    return ()\n'
    ),
    'GO': (
        'package main\n'
        '\n'
        'func main() {\n'
        '\n'
        '}\n'
    ),
    'F95': (
        'program main\n'
        '    implicit none\n'
        '\n'
        'end program main\n'
    ),
    'NASM': (
        'section .text\n'
        'global  _start\n'
        '\n'
        '_start:\n'
        '\n'
        '        mov     eax,    1\n'
        '        xor     ebx,    ebx\n'
        '        int     80h\n'
    ),
    'NASM64': (
        'section .text\n'
        'global  _start\n'
        '\n'
        '_start:\n'
        '\n'
        '        mov     rax,    60\n'
        '        xor     rdi,    rdi\n'
        '        syscall\n'
    ),
    'GAS32': (
        '.intel_syntax noprefix\n'
        '\n'
        '.text\n'
        '.global _start\n'
        '\n'
        '_start:\n'
        '\n'
        '        mov     eax,    1\n'
        '        xor     ebx,    ebx\n'
        '        int     0x80\n'
    ),
    'GAS64': (
        '.intel_syntax noprefix\n'
        '\n'
        '.text\n'
        '.global _start\n'
        '\n'
        '_start:\n'
        '\n'
        '        mov     rax,    60\n'
        '        xor     rdi,    rdi\n'
        '        syscall\n'
    ),
    'GASARM': (
        '.text\n'
        '.global _start\n'
        '\n'
        '_start:\n'
        '\n'
        '        mov     r7,     #1\n'
        '        mov     r0,     #0\n'
        '        swi     0\n'
    ),
    'OCAML': (
        'let () =\n'
        '  ()\n'
    ),
    'TUR': (
        'var line : string\n'
    ),
    'OBJC': (
        '#import <Foundation/Foundation.h>\n'
        '\n'
        'int main(int argc, const char *argv[]) {\n'
        '    NSAutoreleasePool *pool = [[NSAutoreleasePool alloc] init];\n'
        '\n'
        '    [pool drain];\n'
        '    return 0;\n'
        '}\n'
    ),
    'MONOVB': (
        'Imports System\n'
        '\n'
        'Public Module Program\n'
        '    Sub Main()\n'
        '\n'
        '    End Sub\n'
        'End Module\n'
    ),
    'DART': (
        "import 'dart:io';\n"
        '\n'
        'void main() {\n'
        '\n'
        '}\n'
    ),
    'TCL': (
        'proc main {} {\n'
        '\n'
        '}\n'
        '\n'
        'main\n'
    ),
    'CBL': (
        'IDENTIFICATION DIVISION.\n'
        'PROGRAM-ID. MAIN.\n'
        'PROCEDURE DIVISION.\n'
        '    STOP RUN.\n'
    ),
    'MONOFS': (
        'open System\n'
        '\n'
        '[<EntryPoint>]\n'
        'let main argv =\n'
        '    0\n'
    ),
    'SCM': (
        '(import chicken.io)\n'
        '\n'
        '(define (main)\n'
        '  (void))\n'
        '\n'
        '(main)\n'
    ),
    'ADA': (
        'with Ada.Text_IO; use Ada.Text_IO;\n'
        '\n'
        'procedure Main is\n'
        'begin\n'
        '   null;\n'
        'end Main;\n'
    ),
    'AWK': (
        'BEGIN {\n'
        '\n'
        '}\n'
        '\n'
        '{\n'
        '\n'
        '}\n'
        '\n'
        'END {\n'
        '\n'
        '}\n'
    ),
    'COFFEE': (
        'main = ->\n'
        '  return\n'
        '\n'
        'main()\n'
    ),
    'PRO': (
        ':- set_prolog_flag(verbose, silent).\n'
        ":- prompt(_, '').\n"
        ':- use_module(library(readutil)).\n'
        '\n'
        'main :-\n'
        '    halt.\n'
        '\n'
        ':- main.\n'
    ),
    'FORTH': (
        ': main  ( -- )\n'
        ';\n'
        '\n'
        'main\n'
    ),
    'ICK': (
        'DO ,1 <- #13\n'
        'PLEASE DO ,1 SUB #1 <- #238\n'
        'DO ,1 SUB #2 <- #108\n'
        'DO ,1 SUB #3 <- #112\n'
        'DO ,1 SUB #4 <- #0\n'
        'DO ,1 SUB #5 <- #64\n'
        'DO ,1 SUB #6 <- #194\n'
        'PLEASE DO ,1 SUB #7 <- #48\n'
        'DO ,1 SUB #8 <- #26\n'
        'DO ,1 SUB #9 <- #244\n'
        'PLEASE DO ,1 SUB #10 <- #168\n'
        'DO ,1 SUB #11 <- #24\n'
        'DO ,1 SUB #12 <- #16\n'
        'DO ,1 SUB #13 <- #162\n'
        'PLEASE READ OUT ,1\n'
        'PLEASE GIVE UP\n'
    ),
    'BF': (
        '++++++++[>++++[>++>+++>+++>+<<<<-]>+>+>->>+[<]<-]>>.>---.+++++++..+++.>>.<-.<.+++.------.--------.>>+.>++.\n'
    ),
    'SWIFT': (
        'import Foundation\n'
        '\n'
    ),
    'SED': (
        '# sed script\n'
    ),
    'GROOVY': (
        'def main() {\n'
        '\n'
        '}\n'
        '\n'
        'main()\n'
    ),
    'PIKE': (
        'int main() {\n'
        '    return 0;\n'
        '}\n'
    ),
    'SBCL': (
        '(defun main ()\n'
        '  nil)\n'
        '\n'
        '(main)\n'
    ),
    'ZIG': (
        'const std = @import("std");\n'
        '\n'
        'pub fn main() !void {\n'
        '\n'
        '}\n'
    ),
}


def fill_templates(apps, schema_editor):
    Language = apps.get_model('judge', 'Language')
    for key, template in TEMPLATES.items():
        Language.objects.filter(key=key, template='').update(template=template)


def clear_templates(apps, schema_editor):
    Language = apps.get_model('judge', 'Language')
    for key, template in TEMPLATES.items():
        Language.objects.filter(key=key, template=template).update(template='')


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0239_problem_manage_own_submissions_perm'),
    ]

    operations = [
        migrations.RunPython(fill_templates, clear_templates),
    ]
