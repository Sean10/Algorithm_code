# 概念
## `diff`和`merge`是一回事吗?

实际上是两回事.
如果可以通过已知的规则, 比如同时保留双方不一致内容, 自动merge, 那属于`diff`可以做到的内容.
但是如果想要手动`merge`, 比如展示开来, 然后一行行比较人工决定使用哪份, 这个就不属于`diff`提供的功能了, 需要一个展示`diff`结果然后保存回原始文件中的工具, 这个就属于编辑器的范畴了. 像`beyond compare`这种更像是一个集成了差异比较功能的编辑器了.

## `diff`和`patch`和`RCS`版本控制关系?

unified输出的diff就是一个patch, 然后通过patch命令打入. 基于上面的开发出了`Source Code Control System`和`Revision Control System`(RCS).RCS新增了`lock`的功能, 防止文件被其他人checkout之后修改了. 

``` bash
ci a.txt 
#lock
ci -l a.txt 
# checkin
ci -u a.txt
# 查看日志
rlog a.txt
# 获取patch
rcsdiff -u -r1.1 -r1.2 a.txt
```


执行上面的命令就能把文件纳入版本控制, 会在当前目录生成对应文件的管理.

## CVS和Subvision的诞生

中心化版本控制系统

都是通过保存`diff`原型的`changeset`来保存作为日志.

另外增加了`branch`, `trunk`这些概念.

## Git和Mercurial
分布式版本控制系统

基本操作单位从上面的`changeset`变成了`blob`(压缩保存的完整文件). 所以在查询`diff`时是当前做的比较,而不是直接输出结果, `git log --patch`.


# diff
## 支持格式
* 命令模式(normal)
  * ed命令模式
  * RCS(Revision Control System)
* 上下文模式(context)
  * 我们目前默认用的diff和`patch`用的基本都是这个模式的样子.
* unified模式
  * 简化了上下文模式同时显示2个文件的操作, 只显示第一个文件的那些行及要做的操作

## 命令
``` bash
diff -e a.txt b.txt > c.ed
# 输出ed脚本, 可以让a文件和b文件一致.

diff -n a.txt b.txt > c.rcs
# 输出RCS格式的脚本
```


# merge[^5]
`sdiff`和`diff3`之类的支持`merge`的操作.

`diff`自身也支持一定的`if-then-else`的`merge`操作

## 样例文件

### a.txt 
``` 
The Way that can be told of is not the eternal Way;
The name that can be named is not the eternal name.
The Nameless is the origin of Heaven and Earth;
The Named is the mother of all things.
Therefore let there always be non-being,
  so we may see their subtlety,
And let there always be being,
  so we may see their outcome.
The two are the same,
But after they are produced,
  they have different names.
```
### b.txt
```
The Nameless is the origin of Heaven and Earth;
The named is the mother of all things.

Therefore let there always be non-being,
  so we may see their subtlety,
And let there always be being,
  so we may see their outcome.
The two are the same,
But after they are produced,
  they have different names.
They both may be called deep and profound.
Deeper and more profound,
The door of all subtleties!
```
## 自带的配合`C`语言的
``` bash
diff -DTWO a.txt b.txt
```

等价于下面这段,这段等后面的自定义掌握之后比较好看懂.

``` bash
--old-group-format='#ifndef name
%<#endif /* ! name */
' \
--new-group-format='#ifdef name
%>#endif /* name */
' \
--unchanged-group-format='%=' \
--changed-group-format='#ifndef name
%<#else /* name */
%>#endif /* name */
'
```

输出得到的是以第二个文件为基础的`ifndef`之类的分支.

```
#ifndef TWO
The Way that can be told of is not the eternal Way;
The name that can be named is not the eternal name.
#endif /* ! TWO */
The Nameless is the origin of Heaven and Earth;
#ifndef TWO
The Named is the mother of all things.
#else /* TWO */
The named is the mother of all things.

#endif /* TWO */
Therefore let there always be non-being,
  so we may see their subtlety,
And let there always be being,
  so we may see their outcome.
The two are the same,
But after they are produced,
#ifndef TWO
  they have different names.
#else /* TWO */
  they have different names.
They both may be called deep and profound.
Deeper and more profound,
The door of all subtleties!
#endif /* TWO */

```

## group line format (GFMT  GTYPE)

基本上这里的区分主要就是多行匹配和单行匹配的区别了. 和`LFMT`同时运行的时候, 匹配了单行之后, 多行匹配也会触发一次. 具体暂时不知道运行时是先按多行还是单行扫, 总之看到的结果是两项修改均会触发.

主要会有以下几种结果.
* --old-group-format=format
* --new-group-format=format
* --changed-group-format=format
  * 目前来看,如果配置了这条, 则`--new-group-format`基本上会被替换成这个.
  * 只有当这条没设置的时候, 可以让`new`生效.
* --unchanged-group-format=format

``` bash
diff \
   --old-group-format='\begin{old}
%<\end{old}
' \
   --new-group-format='\begin{bf}
%>\end{bf}
' \
--unchanged-group-format='%=' \
   --changed-group-format='\begin{em}
%<\end{em}
\begin{bf}
%>\end{bf}
' \
   a.txt b.txt 


diff \
   --unchanged-group-format='%%' \
   --old-group-format='-------- %dn line%(n=1?:s) deleted at %df:
%<' \
   --new-group-format='-------- %dN line%(N=1?:s) added after %de:
%>' \
   --changed-group-format='-------- %dn line%(n=1?:s) changed at %df:
%<-------- to:
%>' \
   a.txt b.txt > output.4
```

上面这段的`%(n=1?:s)`一开始一点都不理解是啥意思, 突然才反应过来是`line`和`lines`的区别...还以为这个`N`是和前面的`%dn`有关的...

### 格式符
> ‘%<’
> stands for the lines from the first file, including the trailing newline. Each line is formatted according to the old line format (see Line Formats).
> 
> ‘%>’
> stands for the lines from the second file, including the trailing newline. Each line is formatted according to the new line format.
> 
> ‘%=’
> stands for the lines common to both files, including the trailing newline. Each line is formatted according to the unchanged line format.

上面这几个, 分别代表旧文件, 新文件, 两个文件中相同的内容.

> ‘Fn’
> where F is a printf conversion specification and n is one of the following letters, stands for n’s value formatted with F.
> 
> ‘e’
> The line number of the line just before the group in the old file.
> 
> ‘f’
> The line number of the first line in the group in the old file; equals e + 1.
> 
> ‘l’
> The line number of the last line in the group in the old file.
> 
> ‘m’
> The line number of the line just after the group in the old file; equals l + 1.
> 
> ‘n’
> The number of lines in the group in the old file; equals l - f + 1.
> 
> ‘E, F, L, M, N’
> Likewise, for lines in the new file.
> 
> ‘(A=B?T:E)’
> If A equals B then T else E. A and B are each either a decimal constant or a single letter interpreted as above. This format spec is equivalent to T if A’s value equals B’s; otherwise it is equivalent to E.
> 
> For example, ‘%(N=0?no:%dN) line%(N=1?:s)’ is equivalent to ‘no lines’ if N (the number of lines in the group in the new file) is 0, to ‘1 line’ if N is 1, and to ‘%dN lines’ otherwise.

单纯格式符和行号这部分, 基本按照`printf`的使用方式就可以了.

### 输出


```
\begin{old}
The Way that can be told of is not the eternal Way;
The name that can be named is not the eternal name.
\end{old}
The Nameless is the origin of Heaven and Earth;
\begin{old}
The Named is the mother of all things.
\end{old}
\begin{bf}
The named is the mother of all things.

\end{bf}
Therefore let there always be non-being,
  so we may see their subtlety,
And let there always be being,
  so we may see their outcome.
The two are the same,
But after they are produced,
\begin{old}
  they have different names.
\end{old}
\begin{bf}
  they have different names.
They both may be called deep and profound.
Deeper and more profound,
The door of all subtleties!
\end{bf}

```

## Line Format (LFMT LTYPE)
主要做差异有这几种结果. 
* --old-line-format=format
* --new-line-format=format
* --unchanged-line-format=format

``` bash
diff \
   --old-line-format='< %l
' \
   --new-line-format='> %l
' \
   --old-group-format='%df%(f=l?:,%dl)d%dE
%<' \
   --new-group-format='%dea%dF%(F=L?:,%dL)
%>' \
   --changed-group-format='%df%(f=l?:,%dl)c%dF%(F=L?:,%dL)
%<---
%>' \
   --unchanged-group-format='' \
   a.txt b.txt
```

使用这个的时候,发生这样一个问题, 只能看到触发了`--old-group-format`和`--changed-group-format`, 没变化的那种倒是没发现

### 输出

``` 
1,2d0
< The Way that can be told of is not the eternal Way;
< The name that can be named is not the eternal name.
4c2,3
< The Named is the mother of all things.
---
> The named is the mother of all things.
> 
11c10,13
<   they have different names.
---
>   they have different names.
> They both may be called deep and profound.
> Deeper and more profound,
> The door of all subtleties!

```

### 格式符

> In a line format, ordinary characters represent themselves; conversion specifications start with ‘%’ and have one of the following forms.
> 
> ‘%l’
> stands for the contents of the line, not counting its trailing newline (if any). This format ignores whether the line is incomplete; See Incomplete Lines.
> 
> ‘%L’
> stands for the contents of the line, including its trailing newline (if any). If a line is incomplete, this format preserves its incompleteness.
> 
> ‘%%’
> stands for ‘%’.
> 
> ‘%c'C'’
> where C is a single character, stands for C. C may not be a backslash or an apostrophe. For example, ‘%c':'’ stands for a colon.
> 
> ‘%c'\O'’
> where O is a string of 1, 2, or 3 octal digits, stands for the character with octal code O. For example, ‘%c'\0'’ stands for a null character.
> 
> ‘Fn’
> where F is a printf conversion specification, stands for the line number formatted with F. For example, ‘%.5dn’ prints the line number using the printf format "%.5d". See Line Group Formats, for more about printf conversion specifications.

## 自定义需求
### 合并两个文件, 比如跨平台编辑笔记时, 多个文本都出现了新增内容, 同步盘创建了`Conflict`文件的时候

``` bash
diff --old-line-format=%L --new-line-format=%L a.txt b.txt
```

直接双向合并就行了.

# Reference
1. man diff
2. [linux \- Manually merge two files using diff \- Stack Overflow](https://stackoverflow.com/questions/16902001/manually-merge-two-files-using-diff)
3. [用Diff和Patch工具维护源码](https://www.ibm.com/developerworks/cn/linux/l-diffp/?lnk=hmhmhmhm)
4. [版本控制 — Unix 即集成开发环境 1\.0 文档](http://conanblog.me/Unix-as-IDE--Chinese-/revisions.html)
5. [If\-then\-else \(Comparing and Merging Files\)](https://www.gnu.org/software/diffutils/manual/html_node/If_002dthen_002delse.html)