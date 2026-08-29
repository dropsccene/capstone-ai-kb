# Ground Truth 候选 Query（Python 3.14 文档 · 50 条草案）

> 用途：为 kb_1（tutorial + reference，3260 chunks）重建 Recall@K 测试集。
> 流程：你调整 query → 脚本跑检索生成「建议标注」→ 你复核标注 → 存 ground_truth.json → 评测。
> 覆盖：tutorial 15 章 + reference 语言核心。

## 候选清单

| # | query | 预期来源（章/节） |
|---|---|---|
| 1 | 如何启动 Python 解释器并退出交互模式？ | tutorial 1 |
| 2 | Python 中字符串有哪些字面量写法？ | tutorial 2 / reference 词法 |
| 3 | f-string 格式化字符串怎么用？ | tutorial 2 输入输出 |
| 4 | 赋值语句和表达式求值顺序？ | tutorial 2 |
| 5 | if / elif / else 的语法结构？ | tutorial 3 控制流 |
| 6 | for 循环如何遍历字典？ | tutorial 3 |
| 7 | range 函数的三个参数含义？ | tutorial 3 |
| 8 | break 和 continue 的区别？ | tutorial 3 |
| 9 | match 语句支持哪些模式匹配？ | tutorial 3 |
| 10 | 函数定义时如何设置默认参数？ | tutorial 3 |
| 11 | *args 和 **kwargs 是什么？ | tutorial 3 |
| 12 | 列表推导式怎么写？ | tutorial 4 数据结构 |
| 13 | 字典推导式怎么写？ | tutorial 4 |
| 14 | 元组和列表有什么区别？ | tutorial 4 |
| 15 | 集合有哪些常用操作？ | tutorial 4 |
| 16 | import 语句有哪几种形式？ | tutorial 5 模块 |
| 17 | Python 模块搜索路径有哪些？ | tutorial 5 |
| 18 | 包和相对导入怎么用？ | tutorial 5 |
| 19 | 字符串有哪些格式化方法？ | tutorial 6 输入输出 |
| 20 | 如何读写文本文件？ | tutorial 6 |
| 21 | json 模块怎么用？ | tutorial 6 |
| 22 | pickle 和 json 有什么区别？ | tutorial 6 |
| 23 | try except 怎么捕获多个异常？ | tutorial 7 错误异常 |
| 24 | 如何自定义异常类？ | tutorial 7 |
| 25 | raise 语句的用法？ | tutorial 7 |
| 26 | finally 子句的作用？ | tutorial 7 |
| 27 | 如何定义类？类对象和实例对象的关系？ | tutorial 8 类 |
| 28 | Python 继承和多重继承怎么用？ | tutorial 8 |
| 29 | 私有变量和名称改写机制？ | tutorial 8 |
| 30 | 迭代器协议是什么？ | tutorial 8 |
| 31 | 生成器函数怎么写？ | tutorial 8 |
| 32 | yield 和 return 有什么区别？ | tutorial 8 |
| 33 | with 上下文管理器怎么用？ | tutorial 8 |
| 34 | os 模块有哪些常用功能？ | tutorial 9 标准库 |
| 35 | pathlib 和 os.path 的区别？ | tutorial 9 |
| 36 | sys.argv 怎么获取命令行参数？ | tutorial 9 |
| 37 | datetime 模块怎么表示日期？ | tutorial 9 |
| 38 | random 模块有哪些常用函数？ | tutorial 9 |
| 39 | logging 怎么记录日志？ | tutorial 9 标准库 |
| 40 | 如何使用 venv 创建虚拟环境？ | tutorial 12 |
| 41 | pip 常用命令有哪些？ | tutorial 12 |
| 42 | lambda 匿名函数怎么写？ | reference 表达式 |
| 43 | 闭包是什么？ | reference/教程 |
| 44 | 装饰器是什么？ | tutorial 9 |
| 45 | assert 语句的用途？ | reference 简单语句 |
| 46 | del 语句删除变量？ | reference |
| 47 | type 和 isinstance 的区别？ | reference 内置 |
| 48 | 可变类型和不可变类型？ | tutorial 2/4 |
| 49 | Python 标识符命名规则？ | reference 词法 |
| 50 | Python 有哪些关键字？ | reference 词法 |

## 你的任务

1. 增删改查：哪条 query 不合适？缺什么重要主题？（比如 asyncio/正则/类型标注目前在 tutorial/reference 里覆盖弱，可换掉 44/47 等）
2. 确认后我跑检索生成标注建议（50 条，每条 top-10 候选）
3. 你复核「建议标注」→ 我只存你确认的
