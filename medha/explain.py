"""
MEDHĀ IDE — explain.py  — beginner error + crash explainer
===========================================================

WHAT:  Turns a raw compiler message ("'cout' was not declared in this scope") or a
       crash exit code (139, 3221225477) into a short explanation and a fix —
       in English or Hinglish (Roman script), rule-based and fully offline.
WHY:   C-Lite and Dev-C++ show only the raw GCC text; a first-semester student
       does not know what "lvalue required" means. The English tips are ported
       from Kanak's PRABHA (lib/diagnostics.js, lib/crash.js) so both tools teach
       the same thing; the Hinglish lines are written for MEDHĀ.
       Covers GCC/Clang (C, C++), javac and Python tracebacks.
USED BY: runner.py (attaches `tip` to each diagnostic and explains the exit code),
       problems.py (shows the tip column + tooltip).
FLOW:  tip_for(message, lang) → str | None ;  explain_exit(code, lang) → dict | None
"""

import re

# Each entry: (regex, English, Hinglish). First match wins → specific rules first.
TIPS = [
    # Java and Python first: their messages are distinctive, while generic C rules
    # like "division by zero" would otherwise catch a Python ZeroDivisionError.
    # ---------------- Java (javac) ----------------
    (r"class (\w+) is public, should be declared in a file named",
     "A `public class` must be in a file with the same name: `public class Hello` → `Hello.java`.",
     "`public class` usi naam ki file mein hona chahiye: `public class Hello` → `Hello.java`."),
    (r"cannot find symbol",
     "Java does not know this name: check spelling and capital letters (`String`, `System.out.println`), and add the right `import`.",
     "Java ye naam nahi jaanta: spelling aur capital letters check karo (`String`, `System.out.println`), aur sahi `import` jodo."),
    (r"';' expected",
     "A `;` is missing at the end of the statement.",
     "Statement ke end mein `;` chhoot gaya hai."),
    (r"incompatible types: possible lossy conversion",
     "You are storing a bigger type in a smaller one (e.g. `double` → `int`). Add a cast: `int x = (int) d;`",
     "Bade type ko chhote mein rakh rahe ho (jaise `double` → `int`). Cast lagao: `int x = (int) d;`"),
    (r"missing return statement",
     "The method promises to return a value but some path ends without `return`.",
     "Method value return karne ka vaada karta hai par kisi raste par `return` nahi hai."),
    (r"variable (\w+) might not have been initialized",
     "Give the variable a value before reading it, e.g. `int sum = 0;`.",
     "Variable ko padhne se pehle value do, jaise `int sum = 0;`."),
    (r"unreported exception",
     "This call can throw a checked exception. Wrap it in `try { … } catch (IOException e) { … }` or add `throws` to the method.",
     "Ye call checked exception throw kar sakti hai. `try { … } catch (IOException e) { … }` lagao ya method par `throws` likho."),
    (r"reached end of file while parsing",
     "A `}` is missing — the class or a method is never closed.",
     "Ek `}` missing hai — class ya method band nahi hua."),

    # ---------------- Python ----------------
    (r"IndentationError|unexpected indent|expected an indented block",
     "Python uses indentation to group code. Indent the block under `if`/`for`/`def` by 4 spaces, and never mix tabs and spaces.",
     "Python indentation se code group karta hai. `if`/`for`/`def` ke neeche wale block ko 4 spaces andar rakho, tabs aur spaces mix mat karo."),
    (r"NameError: name '(\w+)' is not defined",
     "This name is used before it was created — check the spelling or assign it first.",
     "Ye naam banne se pehle use ho raha hai — spelling check karo ya pehle value assign karo."),
    (r"TypeError: can only concatenate str",
     "You are joining text and a number with `+`. Use `str(n)` or an f-string: `f\"Total: {n}\"`.",
     "Text aur number ko `+` se jod rahe ho. `str(n)` ya f-string use karo: `f\"Total: {n}\"`."),
    (r"ValueError: invalid literal for int\(\)",
     "`int(input())` got text that is not a whole number. Type a number, or handle it with `try/except ValueError`.",
     "`int(input())` ko aisa text mila jo number nahi hai. Number type karo, ya `try/except ValueError` se handle karo."),
    (r"ZeroDivisionError",
     "Division by zero. Check the divisor first: `if b != 0:`.",
     "Zero se divide. Pehle check karo: `if b != 0:`."),
    (r"IndexError: list index out of range",
     "The index is past the end of the list. A list of length n has indexes 0 to n-1.",
     "Index list ke end se aage hai. Length n ki list mein index 0 se n-1 tak hote hain."),
    (r"SyntaxError: (invalid syntax|expected ':')",
     "Python could not read this line — often a missing `:` after `if`/`for`/`def`, or an unclosed bracket or quote.",
     "Python ye line padh nahi paaya — aksar `if`/`for`/`def` ke baad `:` missing, ya bracket/quote band nahi."),
    (r"ModuleNotFoundError: No module named '(\w+)'",
     "This library is not installed. Install it with `pip install <name>` in the terminal.",
     "Ye library install nahi hai. Terminal mein `pip install <name>` se install karo."),
    # ---------------- C / C++ (GCC + Clang wording) ----------------
    (r"(iostream|fstream|iomanip|strstream)\.h['\"]?:? (No such file|file not found)",
     "This is an old Turbo C++ header. Modern C++ drops the `.h`: `#include <iostream>`. MEDHĀ's Turbo mode runs it unchanged, or use Tools → Modernize this code.",
     "Ye purana Turbo C++ header hai. Modern C++ mein `.h` nahi lagta: `#include <iostream>`. MEDHĀ ka Turbo mode ise bina badle chala deta hai, ya Tools → Modernize this code use karo."),
    (r"'(cout|cin|endl|cerr|string|setw|setprecision|vector|getline|fixed)' was not declared|use of undeclared identifier '(cout|cin|endl|cerr|string|setw|setprecision|vector|getline|fixed)'|'(cout|cin|endl)' (is not a member|undeclared)",
     "`cout`, `cin` and `endl` live in the `std` namespace. Write `std::cout`, or add `using namespace std;` after the `#include` lines.",
     "`cout`, `cin`, `endl` `std` namespace ke andar hain. `std::cout` likho, ya `#include` ke baad `using namespace std;` jodo."),
    (r"'::main' must return 'int'|'main' must return 'int'",
     "`void main()` was never valid standard C/C++ (only Turbo C accepted it). Write `int main()`; `return 0;` at the end is optional.",
     "`void main()` standard C/C++ mein kabhi valid nahi tha (sirf Turbo C maanta tha). `int main()` likho; end mein `return 0;` optional hai."),
    (r"'(gets)' was not declared|implicit declaration of function 'gets'|use of undeclared identifier 'gets'",
     "`gets()` was removed in C11/C++14 because it overflows buffers. C++: `std::cin.getline(s, size);`  C: `fgets(s, sizeof s, stdin);`",
     "`gets()` C11/C++14 mein hata diya gaya kyunki ye buffer overflow karta hai. C++: `std::cin.getline(s, size);`  C: `fgets(s, sizeof s, stdin);`"),
    (r"'(clrscr|getch|getche|gotoxy|textcolor|kbhit)' was not declared|implicit declaration of function '(clrscr|getch|getche|gotoxy|textcolor|kbhit)'|use of undeclared identifier '(clrscr|getch|getche|gotoxy|textcolor|kbhit)'",
     "These are Turbo C `conio.h` functions. Add `#include <conio.h>` at the top — MEDHĀ's Turbo mode provides them.",
     "Ye Turbo C ke `conio.h` functions hain. Upar `#include <conio.h>` jodo — MEDHĀ ka Turbo mode inhe deta hai."),
    (r"implicit declaration of function '(\w+)'|call to undeclared function '(\w+)'",
     "This function is used before it is declared. Include the right header (`<stdio.h>` for `printf`, `<string.h>` for `strlen`, `<math.h>` for `sqrt`), or move your function above `main` / add its prototype.",
     "Function declare hone se pehle use ho raha hai. Sahi header include karo (`printf` ke liye `<stdio.h>`, `strlen` ke liye `<string.h>`, `sqrt` ke liye `<math.h>`), ya apna function `main` ke upar le jao / uska prototype likho."),
    (r"expected (?:',' or )?';' (before|after|at end)|expected ';' or ',' (before|after)",
     "A `;` is missing at the end of the previous line. The error is often reported on the line AFTER the mistake — check the line above.",
     "Pichhli line ke end mein `;` chhoot gaya hai. Error aksar galti ke AGLI line par dikhta hai — upar wali line check karo."),
    (r"expected '\}' at end of input|expected '\}'$|expected declaration or statement at end of input",
     "A `{` was never closed. Count the braces of every function, `if`, `for` and `while`.",
     "Koi `{` band nahi hua. Har function, `if`, `for`, `while` ke braces gino."),
    (r"expected '\)'",
     "A `(` was never closed. Count the brackets in the function call or `if (...)`.",
     "Koi `(` band nahi hua. Function call ya `if (...)` ke brackets gino."),
    (r"stray '\\(342|302|303)' in program|non-ASCII characters are not allowed outside of literals",
     "A \"fancy\" character got into the code — usually smart quotes (“ ” ‘ ’) or an en-dash (–) copied from WhatsApp, a PDF or Word. Replace them with plain \" ' -.",
     "Code mein \"fancy\" character aa gaya — aksar WhatsApp, PDF ya Word se copy kiye smart quotes (“ ” ‘ ’) ya dash (–). Inhe normal \" ' - se badlo."),
    (r"missing terminating (\") character|missing terminating ' character",
     "A string's closing `\"` is missing. Every string `\"…\"` must end on the same line.",
     "String ka closing `\"` missing hai. Har string `\"…\"` usi line par khatam honi chahiye."),
    (r"lvalue required as left operand of assignment|expression is not assignable",
     "The left side of `=` must be a variable. If you meant to compare, write `==`.",
     "`=` ke left side mein variable hona chahiye. Compare karna tha to `==` likho."),
    (r"suggest parentheses around assignment used as truth value|using the result of an assignment as a condition",
     "`if (a = 5)` assigns (`=`) instead of comparing (`==`). To compare, write `if (a == 5)`.",
     "`if (a = 5)` value assign karta hai (`=`), compare nahi. Compare ke liye `if (a == 5)` likho."),
    (r"format '%(d|f|c|s|ld|lf)' expects argument of type '(int|float|char|double|long int)\s*\*'|format specifies type '(int|float|char|double)\s*\*'",
     "`scanf` needs the variable's address: `scanf(\"%d\", &x);` — the `&` is missing.",
     "`scanf` ko variable ka address chahiye: `scanf(\"%d\", &x);` — `&` chhoot gaya hai."),
    (r"format '%(d|f|s|c|lf)' expects argument of type|format specifies type",
     "The `printf`/`scanf` format does not match the variable's type: `int` → `%d`, `float` → `%f`, `double` → `%lf` (in scanf), `char` → `%c`, string → `%s`.",
     "`printf`/`scanf` ka format variable ke type se match nahi karta: `int` → `%d`, `float` → `%f`, `double` → `%lf` (scanf mein), `char` → `%c`, string → `%s`."),
    (r"undefined reference to `?'?(Win)?main'?|undefined symbol: _?main",
     "The program has no `main()` function (or it is misspelled, e.g. `Main`). Every C/C++ program needs an `int main()`.",
     "Program mein `main()` function nahi hai (ya spelling galat hai, jaise `Main`). Har C/C++ program ko `int main()` chahiye."),
    (r"undefined reference to|undefined symbol|ld: symbol\(s\) not found",
     "The function is declared but its body (definition) is missing, or its name is misspelled.",
     "Function declare hai par uski body (definition) nahi likhi, ya naam ki spelling galat hai."),
    (r"redefinition of|redeclaration of|conflicting declaration",
     "The same name is declared twice. Declare each variable once, or give the second one a different name.",
     "Ek hi naam do baar declare hua hai. Har variable ek baar declare karo, ya doosre ko alag naam do."),
    (r"conflicting types for",
     "The function's prototype and its definition do not match (return type or parameters differ). Make them the same.",
     "Function ka prototype aur definition match nahi karte (return type ya parameters alag hain). Dono same karo."),
    (r"too few arguments to function|too many arguments to function|no matching function for call",
     "The function needs a different number of arguments (or different types). Check its definition and fix the call.",
     "Function ko alag number (ya type) ke arguments chahiye. Uski definition dekho aur call theek karo."),
    (r"does not name a type|unknown type name",
     "The compiler does not know this type: check the spelling, include the needed header (`<string>` for `string`), or declare the class/struct before using it.",
     "Compiler ye type nahi jaanta: spelling check karo, zaroori header include karo (`string` ke liye `<string>`), ya class/struct use se pehle declare karo."),
    (r"was not declared in this scope|use of undeclared identifier|undeclared \(first use in this function\)|undeclared here",
     "This name is not declared here: check the spelling (C/C++ is case-sensitive — `Sum` ≠ `sum`), whether it is used before its declaration, or outside the `{ }` block it belongs to.",
     "Ye naam yahan declare nahi hai: spelling check karo (C/C++ case-sensitive hai — `Sum` ≠ `sum`), declaration se pehle use to nahi ho raha, ya apne `{ }` block ke bahar to nahi."),
    (r"invalid conversion from 'const char\*' to 'char\*'|ISO C\+\+ forbids converting a string constant to 'char\*'",
     "A string literal (\"hello\") cannot be changed, so it is `const char*`. Write `const char *s = \"hello\";`, or use `std::string`.",
     "String literal (\"hello\") badla nahi ja sakta, isliye woh `const char*` hai. `const char *s = \"hello\";` likho, ya `std::string` use karo."),
    (r"control reaches end of non-void function|non-void function does not return a value",
     "The function returns a value type but some path has no `return`. Return a value on every path.",
     "Function value return karta hai par kisi raste par `return` nahi hai. Har raste par value return karo."),
    (r"division by zero",
     "Division by zero — the program will crash at run time (integers) or give `inf` (floats).",
     "Zero se divide — integers mein program crash hoga, floats mein `inf` aayega."),
    (r"array subscript is (above|below) array bounds|array index \d+ is past the end of the array",
     "An index outside the array's size. For an array of size 10, only indexes 0 to 9 are valid.",
     "Array ke size ke bahar ka index. Size 10 ke array mein sirf 0 se 9 tak index valid hain."),
    (r"unused variable",
     "A variable is declared but never used — only a warning, the program still runs.",
     "Variable declare hua par use nahi hua — sirf warning hai, program phir bhi chalega."),
    (r"comparison of integer expressions of different signedness|comparison of integers of different signs",
     "Comparing `int` with `unsigned` (like `.size()`). Only a warning; use `size_t i` in the loop.",
     "`int` ko `unsigned` (jaise `.size()`) se compare kar rahe ho. Sirf warning; loop mein `size_t i` use karo."),

]

_COMPILED = [(re.compile(rx), en, hi) for rx, en, hi in TIPS]


def _normalise(message):
    """GCC in a UTF-8 locale prints ‘curly’ quotes; patterns use ASCII quotes."""
    return (str(message).replace("‘", "'").replace("’", "'")
            .replace("‛", "'").replace("`", "'").replace("“", '"').replace("”", '"'))


def tip_for(message, lang="en"):
    """Explanation for one compiler/interpreter message, or None if no rule matches."""
    m = _normalise(message)
    for rx, en, hi in _COMPILED:
        if rx.search(m):
            return hi if lang == "hi" else en
    return None


# ---------------------------------------------------------------------------
# Crash explanations (exit code → why + fix). From PRABHA lib/crash.js.
# ---------------------------------------------------------------------------
CRASHES = {
    "SIGSEGV": ("Segmentation fault — the program touched memory it does not own",
                "Usual causes: an array index past its size, an uninitialized or NULL pointer, or a missing `&` in scanf.",
                "Loop conditions check karo (`i < n`, `<=` nahi), pointer ko use se pehle valid address do, scanf mein `&x` likho. Debugger (F5) se crash wali line dekho."),
    "SIGFPE":  ("Arithmetic error — usually integer division by zero",
                "Dividing an integer by 0 (or `%` by 0) makes the CPU stop the program.",
                "Divide karne se pehle check karo: `if (b != 0) c = a / b;`."),
    "SIGABRT": ("The program aborted itself",
                "Usually an `assert()` failed, memory was freed twice, or a C++ exception was not caught.",
                "Output mein aakhri error message padho; exception ho to `try { … } catch (…)` lagao."),
    "SIGILL":  ("Illegal instruction",
                "A non-void function ended without returning a value, or memory got corrupted.",
                "Har non-void function ke har raste par `return` likho. Problems tab ki warnings padho."),
    "SIGBUS":  ("Bus error — invalid memory access",
                "A pointer points to a wrong address — usually a dangling pointer or bad cast.",
                "Pointer kahan se aaya, check karo. Debugger se crash wali line dekho."),
    "STACK":   ("Stack overflow — recursion never stopped (or a huge local array)",
                "A function keeps calling itself and never reaches its base case, or declares something like `int a[1000000];` locally.",
                "Recursion ka base case check karo (`if (n == 0) return …;`). Bade arrays ko `static`/global banao."),
    "DLL":     ("A required DLL was not found",
                "The program depends on a library that is not on this PC.",
                "MEDHĀ Windows par programs `-static` link karta hai; phir bhi aaye to Tools → Toolchains mein bundled compiler chuno."),
    "SIGKILL": ("Program was stopped", "Stop was pressed or the program ran too long.",
                "Infinite loop to nahi? Check karo loop variable sach mein badal raha hai."),
}

NTSTATUS = {0xC0000005: "SIGSEGV", 0xC0000094: "SIGFPE", 0xC0000095: "SIGFPE", 0xC000008E: "SIGFPE",
            0xC000001D: "SIGILL", 0xC0000409: "SIGABRT", 0xC0000374: "SIGABRT", 0xC00000FD: "STACK",
            0xC0000135: "DLL", 0xC0000139: "DLL"}
POSIX_SIGNALS = {11: "SIGSEGV", 8: "SIGFPE", 6: "SIGABRT", 4: "SIGILL", 7: "SIGBUS", 9: "SIGKILL"}
SHELL_CODES = {139: "SIGSEGV", 136: "SIGFPE", 134: "SIGABRT", 132: "SIGILL", 135: "SIGBUS", 137: "SIGKILL"}


def explain_exit(exit_code, crashed=False, windows=False, lang="en"):
    """Explain an abnormal exit. Returns {"name","title","why","fix"} or None.

    exit_code : what QProcess reports
    crashed   : QProcess.ExitStatus.CrashExit (on Linux the code is then the signal number)
    windows   : interpret the code as an NTSTATUS value (0xC0000005 …)
    """
    if exit_code is None:
        return None
    name = None
    if windows:
        name = NTSTATUS.get(exit_code & 0xFFFFFFFF)
    elif crashed:
        name = POSIX_SIGNALS.get(exit_code)
    else:
        name = SHELL_CODES.get(exit_code)
    if not name:
        return None
    title, why_en, fix_hi = CRASHES[name]
    # English text keeps the PRABHA wording; Hinglish mode swaps in the Hinglish fix.
    return {"name": name, "title": title, "why": why_en, "fix": fix_hi if lang == "hi" else _FIX_EN[name]}


_FIX_EN = {
    "SIGSEGV": "Check loop conditions (`i < n`, not `<=`), give pointers a valid address before use, write `&x` in scanf. Run it in the debugger (F5) to see the crashing line.",
    "SIGFPE": "Check before dividing: `if (b != 0) c = a / b;`.",
    "SIGABRT": "Read the last error message in the output; for an exception add `try { … } catch (…)`.",
    "SIGILL": "Add a `return` on every path of every non-void function. Read the warnings in the Problems tab.",
    "SIGBUS": "Check where the pointer came from. Use the debugger to see the crashing line.",
    "STACK": "Check the recursion's base case (`if (n == 0) return …;`). Make big arrays `static` or global.",
    "DLL": "MEDHĀ links programs with `-static` on Windows; if you still see this, pick the bundled compiler in Tools → Toolchains.",
    "SIGKILL": "Is there an infinite loop? Check that the loop variable actually changes.",
}
