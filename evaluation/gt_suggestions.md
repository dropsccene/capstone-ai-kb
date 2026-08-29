# Ground Truth 建议标注（待你复核）

> 用法：逐条看「建议 chunk 的原文预览」，判断它是否**真的回答了**该问题。
> 确认：每条后标注 ✅（建议的 chunk 之一就是答案）或 ✏️ 修改（写正确 chunk id 或「无」）。
> 注意：标注应基于原文语义，不是「检索器给的」——若建议的 chunk 答非所问请换掉。

**Q1.** 如何启动 Python 解释器并退出交互模式？
- chunk_9_1602：inds and loads a module; both a finder and loader object. | interactive | Python has an interactive interpreter wh
- chunk_8_990：. See also interactive. | interpreter shutdown | When asked to shut down, the Python interpreter enters a special 
- chunk_8_869：ommands is not required. | If the new interactive shell is not desired, it can be disabled via the PYTHON_BASIC_

**Q2.** Python 中字符串有哪些字面量写法？
- chunk_9_123：cape | sequences (typically Hexadecimal character or Octal character): | 2.5. String and Bytes literals | 15 |  | The Py
- chunk_9_2023： | string literal, 12 | u" | string literal, 12 | unary | arithmetic operation, 97 | bitwise operation, 97 | unbinding | name,
- chunk_9_1995：token, 7, 117 | None | object, 24, 105 | nonlocal | statement, 115 | not | operator, 102 | not in | operator, 101 | notation, 4 | 

**Q3.** f-string 格式化字符串怎么用？
- chunk_9_128：tted string literal or f-string is a string literal that is prefixed with ‘f’ or ‘F’. These strings may contai
- chunk_9_1482：m: NAME | # LITERALS | # ======== | fstring_middle: | | fstring_replacement_field | | FSTRING_MIDDLE | fstring_replacement
- chunk_9_1485：ent_field: | | '{' annotated_rhs '='? [fstring_conversion] [tstring_full_format_spec] '}' | tstring_middle: | | tstr

**Q4.** 赋值语句和表达式求值顺序？
- chunk_9_1071：s from left to right. Notice that while evaluating an assignment, the right-hand side is | evaluated before the 
- chunk_9_866： is given, they are evaluated from left to right to define the entries of the | dictionary: each key object is u
- chunk_9_1063：ve the lowest priority of all Python operations. | The expression x if C else y first evaluates the condition, C

**Q5.** if / elif / else 的语法结构？
- chunk_9_1971：al, 19 | EAFP, 166 | elif | keyword, 118 | Ellipsis | object, 24 | else | conditional expression, 102 | dangling, 117 | keyword,
- chunk_9_1448：tmt: | | 'elif' named_expression ':' block elif_stmt | | 'elif' named_expression ':' block [else_block] | else_block
- chunk_9_1209：tion: | if_stmt: "if" assignment_expression ":" suite | ("elif" assignment_expression ":" suite)* | ["else" ":" suit

**Q6.** for 循环如何遍历字典？
- chunk_8_121：ting | over an arithmetic progression of numbers (like in Pascal), or giving the user the ability to define both
- chunk_8_673：ter 9. Classes |  | Python Tutorial, Release 3.14.0rc3 | 9.8 Iterators | By now you have probably noticed that most co
- chunk_9_1213：ck to testing the expression. | 8.3 The for statement | The for statement is used to iterate over the elements of 

**Q7.** range 函数的三个参数含义？
- chunk_8_224：they are not available separately, write the function call with the *-operator to unpack the arguments | out of 
- chunk_8_125：ge() Function | If you do need to iterate over a sequence of numbers, the built-in function range() comes in han
- chunk_9_855：ample: [x*y for x in range(10) for y in range(x, x+10)]. | 6.2. Atoms | 87 |  | The Python Language Reference, Release

**Q8.** break 和 continue 的区别？
- chunk_9_1154：s current value. | When break passes control out of a try statement with a finally clause, that finally clause i
- chunk_9_1212：ite of the else clause, if present, is executed and the loop terminates. | A break statement executed in the fir
- chunk_9_1153：ally nested in a for or while loop, but not nested in a function or class definition | within that loop. | It term

**Q9.** match 语句支持哪些模式匹配？
- chunk_9_1259：reak the statement in multiple lines. | µ See also | PEP 343 - The “with” statement | The specification, background,
- chunk_9_1322： | as the keyword. __match_args__[i] must be a string; if not TypeError is raised. | • If there are duplicate keyw
- chunk_9_1291：. The pattern succeeds if the | value found compares equal to the subject value (using the == equality operator)

**Q10.** 函数定义时如何设置默认参数？
- chunk_9_1338：has a default value, all following parameters up until the | “*” must also have a default value — this is a synt
- chunk_9_1339： means | that the expression is evaluated once, when the function is defined, and that the same “pre-computed” v
- chunk_9_1388：s not evaluated when the object is created, but only when the type | parameter’s __default__ attribute is access

**Q11.** *args 和 **kwargs 是什么？
- chunk_9_1654：or example kwargs in the example above. | Parameters can specify both optional and required arguments, as well a
- chunk_9_1653：for example args in the following: | • var-keyword: specifies that arbitrarily many keyword arguments can be pro
- chunk_9_1490：rgs ] | | kwargs | kwargs: | | ','.kwarg_or_starred+ ',' ','.kwarg_or_double_starred+ | | ','.kwarg_or_starred+ | | ','.

**Q12.** 列表推导式怎么写？
- chunk_8_281： | [[1, 5, 9], [2, 6, 10], [3, 7, 11], [4, 8, 12]] | In the real world, you should prefer built-in functions to co
- chunk_8_250：by appending all the items from the iterable. Similar to a[len(a):] = iterable. | list.insert(i, x) | Insert an it
- chunk_9_1214： starred_expression_list expression is evaluated once; it should yield an iterable object. An iterator is | crea

**Q13.** 字典推导式怎么写？
- chunk_8_309：ido': 4127, 'jack': 4098} | In addition, dict comprehensions can be used to create dictionaries from arbitrary k
- chunk_8_308：do', 'irv'] | >>> sorted(tel) | ['guido', 'irv', 'jack'] | >>> 'guido' in tel | True | >>> 'jack' not in tel | False | The d
- chunk_8_941：led a hash in Perl. | dictionary comprehension | A compact way to process all or part of the elements in an iterab

**Q14.** 元组和列表有什么区别？
- chunk_9_535：ct | class itself. Containers usually are sequences (such as lists or tuples) or mappings (like dictionaries), b
- chunk_8_290： in different situations and for different purposes. Tuples | are immutable, and usually contain a heterogeneous
- chunk_8_763：ows an array of numbers stored as two byte unsigned binary numbers (typecode | "H") rather than the usual 16 byt

**Q15.** 集合有哪些常用操作？
- chunk_8_971：an optional if clause. The combined expression generates values for an enclosing | function: | >>> sum(i*i for i i
- chunk_9_231：pt. However, they can be iterated over, and the built-in function len() returns the number of items in a set. | 
- chunk_9_539：lication (meaning repetition) by defining the methods __add__(), | __radd__(), __iadd__(), __mul__(), __rmul__()

**Q16.** import 语句有哪几种形式？
- chunk_9_1984：ct, 26 | immutable types | subclassing, 42 | import | hooks, 75 | statement, 30, 112 | import hooks, 75 | import machinery, 
- chunk_9_814：rt moduleY | from ..subpackage1 import moduleY | from ..subpackage2.moduleZ import eggs | from ..moduleA import foo | 
- chunk_9_684：porting it. The import | statement is the most common way of invoking the import machinery, but it is not the on

**Q17.** Python 模块搜索路径有哪些？
- chunk_9_707：e will be used in various phases of the import search, and it may be the dotted path to a submodule, e.g. | foo.
- chunk_9_788：see the site module) | that should be searched for modules, such as URLs, or database queries. Only strings shou
- chunk_8_1307：7 | open | built-in function, 57 | optimized scope, 128 | P | package, 128 | parameter, 129 | PATH, 45, 115 | path | module sear

**Q18.** 包和相对导入怎么用？
- chunk_8_412： structured into subpackages (as with the sound package in the example), you can use absolute | imports to refer
- chunk_9_1171：empting to | use it in class or function definitions will raise a SyntaxError. | When specifying what module to im
- chunk_8_414：, you might use: | from . import echo | from .. import formats | from ..filters import equalizer | Note that relative 

**Q19.** 字符串有哪些格式化方法？
- chunk_8_1073：nts (in range U+0000–U+10FFFF). To store or transfer | a string, it needs to be serialized as a sequence of byte
- chunk_8_438：nd characters within them (called format fields) are replaced with the objects passed into the str. | format() m
- chunk_8_446：12 | 9 | 81 | 729 | 10 100 1000 | For a complete overview of string formatting with str.format(), see formatstrings. | 7.1

**Q20.** 如何读写文本文件？
- chunk_8_456： | Normally, files are opened in text mode, that means, you read and write strings from and to the file, which a
- chunk_8_468：le newline. | >>> f.readline() | 'This is the first line of the file.\n' | >>> f.readline() | 'Second line of the file
- chunk_8_482：mply serializes the object to a text file. So if f is a text | file object opened for writing, we can do this: | j

**Q21.** json 模块怎么用？
- chunk_8_1304：, 87 | I | IDLE, 125 | immortal, 125 | immutable, 125 | import path, 125 | importer, 125 | importing, 125 | interactive, 125 | i
- chunk_8_722：ck- | age has a complete toolset for building or decoding complex message structures (including attachments) and
- chunk_8_484：reference for the json module contains an explanation of this. | µ See also | pickle - the pickle module | Contrary 

**Q22.** pickle 和 json 有什么区别？
- chunk_8_484：reference for the json module contains an explanation of this. | µ See also | pickle - the pickle module | Contrary 
- chunk_8_1304：, 87 | I | IDLE, 125 | immortal, 125 | immutable, 125 | import path, 125 | importer, 125 | importing, 125 | interactive, 125 | i
- chunk_8_485：unicate with applications written in other languages. It | is also insecure by default: deserializing pickle dat

**Q23.** try except 怎么捕获多个异常？
- chunk_9_1563：ributes and catches exceptions if the assumption proves false. This clean and fast style is | characterized by t
- chunk_8_548：or 1 | +---------------- 2 ---------------- | | SystemError: error 2 | +------------------------------------ | >>> try
- chunk_8_500：n occurs which does not match the exception named in the except clause, it is passed on to outer | try statement

**Q24.** 如何自定义异常类？
- chunk_8_527：tin-exceptions. | 8.6 User-defined Exceptions | Programs may name their own exceptions by creating a new exception
- chunk_9_1141： class, the value is the instance itself. | A traceback object is normally created automatically when an excepti
- chunk_9_604： | For custom classes, implicit invocations of special methods are only guaranteed to work correctly if defined 

**Q25.** raise 语句的用法？
- chunk_9_1138： sufficient to cause that definition to create a generator | function instead of a normal function. | For full det
- chunk_9_1434： '**=' | | '//=' | return_stmt: | | 'return' [star_expressions] | (continues on next page) | 145 |  | The Python Language Re
- chunk_9_1139：are present, raise re-raises the exception that is currently being handled, which is also known as | the active 

**Q26.** finally 子句的作用？
- chunk_9_1246：e last return statement executed. Since the finally clause | always executes, a return statement executed in the
- chunk_8_539：ted in any event. The TypeError raised by dividing two strings is not | handled by the except clause and therefo
- chunk_8_531：a finally clause is present, the finally clause will execute as the last task before the try statement complet

**Q27.** 如何定义类？类对象和实例对象的关系？
- chunk_9_504：class object is the one that will be referenced by the zero-argument form of super(). __class__ is an implicit
- chunk_8_623：instance is referenced, the instance’s class is | searched. If the name denotes a valid class attribute that is 
- chunk_9_320：ple: | >>> class A: pass | >>> class B(A): pass | >>> A.__subclasses__() | [<class 'B'>] | 3.2.11 Class instances | A clas

**Q28.** Python 继承和多重继承怎么用？
- chunk_8_653：, int) is True since bool is a subclass | of int. However, issubclass(float, int) is False since float is not a 
- chunk_8_658：m object, so any case of multiple inheritance provides more than one path to reach | object. To keep the base cl
- chunk_9_1502：at don’t inherit from a class but are still recognized by isinstance() and | issubclass(); see the abc module do

**Q29.** 私有变量和名称改写机制？
- chunk_8_664：ling specifications for details and special cases. | Name mangling is helpful for letting subclasses override me
- chunk_8_660：ritance. For | more detail, see python_2.3_mro. | 9.6 Private Variables | “Private” instance variables that cannot b
- chunk_8_667：ass and _MappingSubclass__update in the | MappingSubclass class respectively. | Note that the mangling rules are d

**Q30.** 迭代器协议是什么？
- chunk_9_714：le. This protocol consists of two conceptual objects, finders and loaders. A finder’s job is to determine whet
- chunk_8_1049：o find a backwards compatible resolution to any identified problems. | This process allows the standard library 
- chunk_9_1664：he inclusion of the API. | Even for provisional APIs, backwards incompatible changes are seen as a “solution of 

**Q31.** 生成器函数怎么写？
- chunk_8_680：n rev: | print(char) | m | a | p | s | 9.9 Generators | Generators are a simple and powerful tool for creating iterators. Th
- chunk_9_910：erator = echo(1) | >>> print(next(generator)) | Execution starts when 'next()' is called for the first time. | 1 | >>>
- chunk_8_681：re | it left off (it remembers all the data values and which statement was last executed). An example shows that

**Q32.** yield 和 return 有什么区别？
- chunk_9_916：t another | external call. The value of the yield expression after resuming depends on the method which resumed 
- chunk_9_886：tate | of any exception handling. When the execution is resumed by calling one of the generator’s methods, the f
- chunk_9_1135：ator function, an empty return statement indicates that the asynchronous generator is | done and will cause Stop

**Q33.** with 上下文管理器怎么用？
- chunk_9_1250：ment with one “item” proceeds as follows: | 1. The context expression (the expression given in the with_item) is
- chunk_9_583：ntime context for the execution of the | block of code. Context managers are normally invoked using the with sta
- chunk_8_733： a simplified syntax suitable for editing by end-users. | This allows users to customize their applications with

**Q34.** os 模块有哪些常用功能？
- chunk_9_2003：ath based finder, 80, 173 | path entry, 173 | path entry finder, 173 | path entry hook, 173 | path hooks, 75 | path-like
- chunk_8_689： os module provides dozens of functions for interacting with the operating system: | >>> import os | >>> os.getcwd
- chunk_8_691：tive aids for working with large modules like os: | >>> import os | >>> dir(os) | <returns a list of all module func

**Q35.** pathlib 和 os.path 的区别？
- chunk_9_1658：ementing the os.PathLike protocol. An object that supports the os.PathLike | protocol can be converted to a str 
- chunk_9_1657：a specific path entry. | path based finder | One of the default meta path finders which searches an import path fo
- chunk_8_1042：ct representing a file system path. A path-like object is either a str or bytes object representing | a path, or

**Q36.** sys.argv 怎么获取命令行参数？
- chunk_8_694：te as a list. For instance, let’s take the following demo.py file: | 87 |  | Python Tutorial, Release 3.14.0rc3 | # Fi
- chunk_8_352：port sys | fib(int(sys.argv[1])) | you can make the file usable as a script as well as an importable module, becau
- chunk_8_351：cripts | When you run a Python module with | python fibo.py <arguments> | the code in the module will be executed, j

**Q37.** datetime 模块怎么表示日期？
- chunk_9_144：lue:{width}.{precision}}" | # nested fields | 'result: | 12.35' | >>> today = datetime(year=2017, month=1, day=27) | >>>
- chunk_8_709：one aware. | >>> # dates are easily constructed and formatted | >>> from datetime import date | >>> now = date.today
- chunk_8_707：> server.sendmail('soothsayer@example.org', 'jcaesar@example.org', | >>> server.quit() | (Note that the second exa

**Q38.** random 模块有哪些常用函数？
- chunk_9_1764：ying the random module includes code based on a download from http://www.math. | sci.hiroshima-u.ac.jp/~m-mat/MT
- chunk_8_701：access to the underlying C library functions for floating-point math: | 88 | Chapter 10. Brief Tour of the Standar
- chunk_8_703：.0, 1.0) | 0.17970987693706186 | >>> random.randrange(6) | # random integer chosen from range(6) | 4 | The statistics mo

**Q39.** logging 怎么记录日志？
- chunk_8_755：sage priority: DEBUG, INFO, WARNING, ERROR, and CRITICAL. | The logging system can be configured directly from P
- chunk_8_752：ing | The logging module offers a full featured and flexible logging system. At its simplest, log messages are s
- chunk_8_143：d: | >>> def initlog(*args): | pass | # Remember to implement this! | as a placeholder body as well. See bltin-ellipsi

**Q40.** 如何使用 venv 创建虚拟环境？
- chunk_8_784： a copy | of the Python interpreter and various supporting files. | A common directory location for a virtual envi
- chunk_8_783：al environment, decide upon a directory where you want to place it, and run the venv module as a | script with t
- chunk_8_782：ule used to create and manage virtual environments is called venv. venv will install the Python version | from w

**Q41.** pip 常用命令有哪些？
- chunk_8_789： called pip. By default pip will install packages from | the Python Package Index. You can browse the Python Pac
- chunk_8_797：-env) $ python -m pip list | novas (3.1.1.3) | numpy (1.9.2) | pip (7.0.3) | requests (2.7.0) | setuptools (16.0) | python
- chunk_9_2004：ilt-in function, 57, 58 | power | operation, 97 | precedence | operator, 104 | primary, 93 | print | built-in function, 43 | p

**Q42.** lambda 匿名函数怎么写？
- chunk_9_1064：conditional expressions. | 6.14 Lambdas | lambda_expr: "lambda" [parameter_list] ":" expression | Lambda expressions
- chunk_9_1347： the form “*identifier” may have an annotation “: *expression”. See | PEP 646. | It is also possible to create ano
- chunk_8_1004：ambda | An anonymous inline function consisting of a single expression which is evaluated when the function is c

**Q43.** 闭包是什么？
- chunk_9_243：les – the global namespace of the | module in which the function was defined. | function.__closure__ | None or a tup
- chunk_9_755：tlib APIs, the import or import-from statements, | or built-in __import__()) a binding is placed in the parent m
- chunk_8_973：pe hints and | annotations. | For more details, see generic alias types, PEP 483, PEP 484, PEP 585, and the typing

**Q44.** 装饰器是什么？
- chunk_8_935：ore objects that reference each other in a reference cycle, but are not referenced by | objects outside the grou
- chunk_9_1550：a reference cycle, but are not referenced by | objects outside the group. The goal of the cyclic garbage collect
- chunk_9_180： decorators. | For some tokens, the distinction is unclear. For example, some people consider ., (, and ) to be 

**Q45.** assert 语句的用途？
- chunk_9_1949：nt, 112 | keyword, 112, 119, 122, 123 | match statement, 123 | with statement, 122 | AS pattern, OR pattern, capture p
- chunk_9_1123：ations are never evaluated. | 7.3 The assert statement | Assert statements are a convenient way to insert debuggin
- chunk_9_1213：ck to testing the expression. | 8.3 The for statement | The for statement is used to iterate over the elements of 

**Q46.** del 语句删除变量？
- chunk_8_284：4.5] | >>> del a[:] | >>> a | [] | del can also be used to delete entire variables: | >>> del a | Referencing the name a h
- chunk_8_282：acking Argument Lists for details on the asterisk in this line. | 5.2 The del statement | There is a way to remove
- chunk_9_396：__del__(). | • __del__() can be executed during interpreter shutdown. As a consequence, the global variables | it 

**Q47.** type 和 isinstance 的区别？
- chunk_9_1316：nce of the builtin type , raise TypeError. | 2. If the subject value is not an instance of name_or_attr (tested 
- chunk_8_652：) | Python has two built-in functions that work with inheritance: | • Use isinstance() to check an instance’s type
- chunk_9_516：e instance is itself a class. | µ See also | PEP 3119 - Introducing Abstract Base Classes | Includes the specificati

**Q48.** 可变类型和不可变类型？
- chunk_9_185：Like its identity, an object’s type is also unchangeable.1 | The value of some objects can change. Objects whose
- chunk_9_221：bility: | 3.2. The standard type hierarchy | 25 |  | The Python Language Reference, Release 3.14.0rc3 | Immutable sequen
- chunk_9_187：n unchangeable value, it is more subtle.) An object’s mutability is determined by its type; for instance, | numb

**Q49.** Python 标识符命名规则？
- chunk_8_247： | method argument (see A First Look at Classes for more on classes and methods). | • Don’t use fancy encodings if
- chunk_8_733： a simplified syntax suitable for editing by end-users. | This allows users to customize their applications with
- chunk_9_1458：0. Full Grammar specification |  | The Python Language Reference, Release 3.14.0rc3 | (continued from previous page)

**Q50.** Python 有哪些关键字？
- chunk_9_1982：tion, 40 | hash | built-in function, 44 | hash character, 7 | hash-based pyc, 168 | hashable, 89, 168 | hexadecimal litera
- chunk_9_1995：token, 7, 117 | None | object, 24, 105 | nonlocal | statement, 115 | not | operator, 102 | not in | operator, 101 | notation, 4 | 
- chunk_8_1310：IC_REPL, 115 | PYTHON_GIL, 124 | Pythonic, 130 | PYTHONPATH, 45, 46 | PYTHONSTARTUP, 116 | Q | qualified name, 130 | R | refer
