---
abc
---


`123`


1123 | 123
-- | --
123<br/>45 | 23

<heading>123</heading>

<h1>
  <img src="https://raw.githubusercontent.com/micromark/micromark/2e476c9/logo.svg?sanitize=true" alt="micromark" />
</h1>


<br/>


*bbbs*

# **1** *2*
## 2 `q123`

### 3
#### 45

##### 5

###### 6      111111111111111  `wewew`

### bb
12
123 111111111111111111`1234`
$a=b$



a
----



$$a<bb=cc=d>e$$


``` mermaid
graph TD;
    A-->B;
    A-->C;
    B-->D;
    C-->D;

```

[剩余参数 \- JavaScript \| MDN](https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Reference/Functions/Rest_parameters)


![](https://bean-li.github.io/assets/ceph_internals/ceph_mon_paxosservice.png)

![](test/test_2021-09-22-23-23-12.png)


# 理解

`markdown`是有对应的标准的. 似乎这篇可以参考?

下面todo中提到的一些`list`的识别场景, 其实这篇`spec`有做一定的边界澄清?


[CommonMark Spec](https://spec.commonmark.org/0.30/)

[中文版CommonMark Spec](http://yanxyz.github.io/commonmark-spec/)

# Issue
## quote之后的内容导致卡顿

疑似是我行的长度过长之后的渲染就会比较卡顿? 至少滚动就不流畅了.

应该是`blockquote`这段的. 

但是卡顿这个我怎么排查是哪的呢? 好像是css切换那块的. 我把`filter`换掉能不能解决呢?

去掉`filter`的渲染之后就正常了.

## 拆分无序列表和有序列表的渲染

### 理解
`state.offset`用途?

`ListItems`是哪里得到的`type`?

好像某个第三方库的, 不是这套代码里的.

搜一下.

疑似是来自这段的.

```
const parser = require('unified')()
    .use(require('remark-math'))
    .use(require('remark-parse'))
    .use(require('remark-gfm'))
    .parse;
```

嗯, 没错, 应该是`remark`这个`markdown`解析库里的`listitem`.

怎么区分有序列表和无序列表呢?


根据下面这段, 一开始`type`为`list`, 具有`ordered`属性, `children`中才是具体的列表内容.

所以如果要改, 预计需要在判断`listitem`前就进行区分处理.
```
 {
      "type": "list",
      "ordered": true,
      "start": 1,
      "spread": true,
      "children": [
        {
          "type": "listItem",
          "spread": false,
          "checked": null,
          "children": [
            {
              "type": "paragraph",
              "children": [
                {
                  "type": "text",
                  "value": "First",
                  "position": {
                    "start": {
                      "line": 71,
                      "column": 4,
                      "offset": 437
                    },
                    "end": {
                      "line": 71,
                      "column": 9,
                      "offset": 442
                    }
                  }
                }
              ],
              "position": {
                "start": {
                  "line": 71,
                  "column": 4,
                  "offset": 437
                },
                "end": {
                  "line": 71,
                  "column": 9,
                  "offset": 442
                }
              }
            }
          ],
          "position": {
            "start": {
              "line": 71,
              "column": 1,
              "offset": 434
            },
            "end": {
              "line": 71,
              "column": 9,
              "offset": 442
            }
          }
        },
        {
          "type": "listItem",
          "spread": false,
          "checked": null,
          "children": [
            {
              "type": "paragraph",
              "children": [
                {
                  "type": "text",
                  "value": "Second",
                  "position": {
                    "start": {
                      "line": 73,
                      "column": 4,
                      "offset": 447
                    },
                    "end": {
                      "line": 73,
                      "column": 10,
                      "offset": 453
                    }
                  }
                }
              ],
              "position": {
                "start": {
                  "line": 73,
                  "column": 4,
                  "offset": 447
                },
                "end": {
                  "line": 73,
                  "column": 10,
                  "offset": 453
                }
              }
            }
          ],
          "position": {
            "start": {
              "line": 73,
              "column": 1,
              "offset": 444
            },
            "end": {
              "line": 73,
              "column": 10,
              "offset": 453
            }
          }
        },
```

todo: `extension.js`里`start`和`end`和`node`这几个参数哪里传进来的呢?

现阶段传入的每个`node`, ordered属性并不在单个上面.

预计需要改成三层

* list
  * chilren
    * listItem
      * children
        * paragraph


无序的则是
* listItem
  * chilren
    * paragraph

或者
* listItem
  * children
    * paragraph
    * list
      * children
        * listItem
          * children
            * paragraph

存在多层关联的这种.不能直接以node的type来区分了.

这个节点的遍历关系? 是DFS还是BFS?

目前并没有找到


## 增加http链接图片支持

只是单纯的增加`http`的`schema`的透传就可以, 剩下的交给`vscode`自身支持


## 修复`latex`显示的渲染结果太小的问题

用`Elements`定位了下, 实际上是`svg`渲染的图片的渲染尺寸不对.

大致是通过 html/svg+xml base64 渲染 svg.

通过在ebfore元素里增加`url`的`content`.

把SVG代码直接内联在CSS的url()方法中

这个逻辑里可能之所以会根据行的数量来决定要渲染的长度, 应该是为了确保不会点到后面的空行, 结果触发的是这行的内容?

这个的做法是不是弄成自动收缩这几行更好?

mermaid的图也有同样的问题.

### 分析lineHeight
首先, 我的配置中默认`lineHeight`是设置为`0`的, 所以走的下面这个逻辑

> Use 0 to automatically compute the line height from the font size.
> Values between 0 and 8 will be used as a multiplier with the font size.
> Values greater than or equal to 8 will be used as effective values.

根据这个, 所以跟`font size`应该是成成比例的.

``` js
    const lineHeight = vscode.workspace.getConfiguration("editor").get("lineHeight", 0);
    // https://github.com/microsoft/vscode/blob/45aafeb326d0d3d56cbc9e2932f87e368dbf652d/src/vs/editor/common/config/fontInfo.ts#L54
    if (lineHeight === 0) {
        state.lineHeight = Math.round(process.platform == "darwin" ? 1.5 * state.fontSize : 1.35 * state.fontSize);
    } else if (lineHeight < 8) {
        state.lineHeight = 8;
    }
```

的确, 发现这段代码这里`lineHeight`只得到了2, 大概是这里写错了. 可能作者不是`darwin`平台的, 所以感知不到.



## 多行的`latex`除了按行数整比放大代码之外, 是否有正常的方式折叠到那几行?

* collapse
* folding


* FoldingRange
* registerFoldingRangeProvider
  
Todo:怎么找不到`javascript`如何使用`FoldingRangeProvider`的呢...

使用方式类似下面这样:
``` javascript
context.subscriptions.push(vscode.languages.registerFoldingRangeProvider('markdown', {
		provideFoldingRanges: (document, context, _) => {
		console.log(document.languageId);
		console.log("try to folding range");
		let ranges = []
		const temp = new vscode.FoldingRange(1, 50, vscode.FoldingRangeKind.Comment);
		ranges.push(temp);
		return ranges
	}}));
```

`context.subscriptions.push`如何理解?

是不是这个只是用在当我即将触发`folding`的时候, 才会进入这个函数逻辑? 确实, 比如我设置`kind`为`Comment`的时候, 触发`Fold all comments`就能够把我标记的范围给圈起来.

所以自动圈, 应该不是这个函数


## fold/unfolder API?
目前根据这个[\[folding\] API for programmatically folding lines · Issue \#37682 · microsoft/vscode](https://github.com/microsoft/vscode/issues/37682)来看似乎是不存在的.

根据[Built\-in Commands \| Visual Studio Code Extension API](https://code.visualstudio.com/api/references/commands)这篇里的`editor.fold`

发现还是文档里没写清楚参数的数据结构, 搜代码样例从这里找到的[autofold/extension\.ts at c721aa8b616060624b107cbdd44c44ec4827adec · TigerGold59/autofold](https://github.com/TigerGold59/autofold/blob/c721aa8b616060624b107cbdd44c44ec4827adec/src/extension.ts)

实际使用方式是类似这种
``` js
vscode.commands.executeCommand('editor.fold', {"selectionLines": [1]});
```

## wrod wrap折叠后的后面几行开头无渲染效果

比如`quote`的特殊符号仅第一行有.

## 修复[When the cursor is in the line of heading, should it show '\#' at the begining of the line? · Issue \#10 · Sean10/markless](https://github.com/Sean10/markless/issues/10)

2组rangeBehavior目前没有办法合并.

当处在中间时, 没有办法让左侧的识别到右侧的参与.

左侧的隐藏, 右侧的需要放大

* 鼠标在这行上时, 希望所有效果全部取消. 直到`cursor`离开该行
* 目前效果: 
    * 右侧的渲染: 鼠标在行末, 取消了放大效果. 鼠标在heading的左侧离开时, 重新恢复放大效果
    * 左侧的渲染: 鼠标在行末甚至`heading`期间, 依旧不显示
      * 指针直到接近`# `的范围, 才取消隐藏.
* 考虑增加一个覆盖的操作, 当鼠标出现在这个范围内, 取消所有的装饰器. 但是条件必须是这个触发效果在最后. 从而覆盖掉另外俩装饰效果.

考虑咨询下这个的效果[兄弟萌，让我们在 Vscode 里放烟花吧 \- 51CTO\.COM](https://developer.51cto.com/art/202106/668897.htm)

似乎他对这个range使用比较熟练.

如果我这个后加, 应该就有效了把?

> A TextEditorDecorationType is a disposable which can be removed/releaded by calling its dispose-method
好像有清理的逻辑?

我先试试现在这套代码的pop逻辑?pop 不行, 我需要的是清理掉对应的decoration. 而不是现在的这种.

可以考虑增加一个清理掉所有的css的装饰, 在鼠标在上面时触发, 离开时, 这个效果被清理掉.

如果用dispose, 那所有的装饰器的变量也释放了, 如果要用这个, 那就必须要把每个heading 维护一个单独的装饰器, 否则就一起被释放了.


所以最好是有一个disable的方法, 比如从队列里去掉这个. 可能维护一张map, 或者这个列表里就自带了行号的属性, 这样就能够比较当前行是不是其中一个了.

官方的2个方法:[Remove decoration type · Issue \#22 · microsoft/vscode\-extension\-samples](https://github.com/microsoft/vscode-extension-samples/issues/22)
> option1 to nuke all uses of a certain decoration type across all editors is decType.dispose()
> option2 to nuke all uses of a certain decoration type in a single editor instance is editor.setDecorations(decType, [])

好像`memoize`这个函数还做了缓存加速.


好像代码里用的是offset, 而不是Range. 这样的话的确没有`line`属性了.

这是原生的`decorationRanges`的限制吗? 之前好像没看到这种要求. `Range`噢, 2种构造函数而已.

todo:成功了. 不过好像`enlarge`那个, 因为指针一移动, 又加回去了的样子? 这个明天再修一下.

## heading的字体放大, 似乎其实也可以接着放大. 好像行的高度, 会跟着我的指定的字体大小变大而变大

所以并不是我一开始理解的字体大小默认设置14, 这个行就只能容纳14的情况.

## heading的隐藏存在一个问题, 凡是在标题上触发的其他模式的渲染, 依旧会存在渲染错的问题, 清理可能需要考虑取消所有该位置的渲染.

是通过反查? 还是通过map出来之后, 检查?

## `block quote`存在2个渲染问题
### 位置, 依旧是按照未隐藏`#`来的

可能需要梳理一下, 这种怎么让多种模式能够复用一套清理逻辑?

怎么获取到对应的字的宽度呢? 毕竟不是以类型来显示`node`, 而是反过来拆解的.

是否可以引入关联性呢? 毕竟本身是存在`children`的概念的, 只是在子节点的时候, 不知道怎么访问到父亲节点的内容.

如果增加父亲节点的访问链接, 那就可以迭代父节点, 是否存在其他属性需要渲染了 ? 这样的话, 就可以按顺序一个个处理了? 这个好像其实就是迭代顺序? 只是后接收到的处理的数据依旧是原始数据, 而不是上级已经处理过后的数据?

目前是按照`visit`的顺序. 如果让每次visit之后, 使用的数据也进行更新呢? 这样的话, 其实会在原始的数据里增加好几个链接? 

#### 思路
* 修改visit之后, 使用的node数据来源? 或者增加基础属性? 比如font等?
* 修改数据结构? 从map改为链表关系? map之间其实是可以营造链表效果的.
* 暂时沿用之前那个修改`listItem`的思路, 直接在visite的时候, 把上层的`depth`赋给子节点.
#### 暂时沿用之前那个修改`listItem`的思路, 直接在visite的时候, 把上层的`depth`赋给子节点.

目前存在的问题: 位置是移动了, 但是好像还有一层外圈没跟着移动? 怀疑不是`inlineCode`的装饰.  的确, 注释掉这个处理之后, 还存在. 怀疑是其他插件的. 确实, `markdown_all_in_one`里的...

那如果我解决了这个问题, 可能还需要考虑那边如何关闭? 毕竟挺多快捷键依赖那个的...

先试试吧.

另外, 这里如果成功了, 还需要考虑`inlineCode`在进入该行时, 自动被消除的操作.

另外, 似乎大小也并没有跟着变...

优先尝试解决border的`size`的问题吧?

[Border do not match correctly if the font size if too big or small · Issue \#33 · leodevbro/vscode\-blockman](https://github.com/leodevbro/vscode-blockman/issues/33)
根据这个来看, 好像是根据`lineHeight`来的? 虽然`fontSize`大的时候好像把`lineHeight`也撑大了, 但是看起来`border`没有变. 根据这个的意思, 好像可以把`fontSize`调大, 然后影响border. 不过这块有点不理解, 为啥目前`fontSize`已经大了, 并没有正常呢?

试了下, 直接在元素上加`border`属性是能够按照字体大小扩大`border`的. 所以问题就在于现在背景上显示的`border`到底绑定在哪个元素上.

奇怪, 为什么全局搜索, 在`html`的这个总元素上搜到的呢? 而且调整一点用都没有...

todo:现在的核心痛点就是怎么找到这个`border`的`css`设置. 不在默认点击找到的`div`属性里, 因为删掉该行依旧存在. 好像确实很难找到. 不知道chrome为啥有的css就找不到呢? 之后再看看

`view-overlays`? 

终于一个个找找到的`<div class="cdr ced-1-TextEditorDecorationType10-0" style="left:0px;width:36px;height:18px;"></div>`


.monaco-editor .ced-1-TextEditorDecorationType10-0

ced-1-TextEditorDecorationType10-0
奇怪, 这个class的`css`在哪?

手动逐个删除二分定位是找到了

但是在哪呢?

`vscode createTextEditorDecorationType view-overlays`

什么情况下, 装饰器会被添加到一个独立的div里呢? 为啥不复用文本的那部分呢?

`export class ViewOverlays extends ViewPart implements IVisibleLinesHost<ViewOverlayLine> {`

-> `ContentViewOverlays`

const contentViewOverlays = new ContentViewOverlays(this._context);

export class View extends ViewEventHandler {

这里构造的时候就能看到了.

		contentViewOverlays.addDynamicOverlay(new CurrentLineHighlightOverlay(this._context));
		contentViewOverlays.addDynamicOverlay(new SelectionsOverlay(this._context));
		contentViewOverlays.addDynamicOverlay(new IndentGuidesOverlay(this._context));
		contentViewOverlays.addDynamicOverlay(new DecorationsOverlay(this._context));

怀疑进到不同的渲染里了?

好像view-overlays是属于标准的?不对

一个是`view-lines` 是我之前那几个元素的. `view-overlays`是那几个Css渲染的...基本上目前只看到`border`会进这里.

Todo: 忽然想到一个猜测点. 由于html的正文始终只有一份, 会不会是如果对一个range存在多个css的装饰器, 则会把新增的装饰器添加到`view-overlays`里. 

todo: 但是理论上其实是可以做到识别用户插入的多个装饰器, 然后对Range进行拆分的吧? 拆分到比如以1个字符为单位, 然后重叠装饰器.

可以验证下, 是哪种. 这块不知道官方文档里有没有提到.

emm, `*`和`**`并没有进入到view-overlays, 依旧在view-lines

TODO: 还是说仅限于`border`这种参数才会被放到overlays?

尝试了, `outline`也被加到`overlays`里了, 而`top`虽然是同一个装饰器塞入的, 这个操作被放到了`view-lines`里. 所以初步怀疑是根据属性划分? 明明可以把`border`属性直接绑在对应的位置, 为啥非得拆到`overlays`里呢?

应该是了, 这行单纯只有`border`属性,同样也是被加在`overlays`范畴.

目前, 位置对上了. 但是因为和字体大小不匹配, 还是会存在丢失的情况.

TODO:把判定当前行进入修改的逻辑封装为函数比较好.

在`View`构造的时候, 会构造`ViewLines`和`ViewOverlays`

好像是在`registerThemingParticipant`这里触发的?

`.monaco-editor .ced-1-TextEditorDecorationType10-0`, 注册时应该是`.ced-`这个关键词

走的这个`CSSNameHelper`...这样的话, 就没

`cdr`呢? 具体的`div`上有这个`class`

在`DecorationsOverlay`的`_renderNormalDecoration`

是这条`contentViewOverlays.addDynamicOverlay(new DecorationsOverlay(this._context));`

`ViewOverlays`->`prepareRender`


`viewPart.prepareRender(renderingContext);`

好像接下来就是`ViewImpl`里的触发渲染条件调用的了.

那现在问题就是那个`border`参数是什么时候被传递进来的了? 我应该使用的是`createTextEditorDecorationType`的`state.activeEditor.setDecorations`

一时这个好像没找到到底做了什么

从这里添加`DecorationsOverlay`啥都没找到,  直接用的`const className = d.options.className!;`

`let decorations: ViewModelDecoration[] = [], decorationsLen = 0;`

`const _decorations = ctx.getDecorationsInViewport();`

TODO:好像走到了这段`_getDecorationsViewportData`, 这里是不是就是我需要知道的区分`border`和`textDecoration`的地方?

`		const renderingContext = new RenderingContext(this._context.viewLayout, viewportData, this._viewLines);`



### 大小, 也是按照字体的初始大小, 而不是渲染后的大小来的.

* 是否能够感知当前行已经渲染的字体大小等参数, 然后基于这个做二次渲染呢?

毕竟完全是存在特效重叠的情况的.

翻了下文档, `border`好像没有`size`的调整属性. 那是否这个就是限制呢? 感觉不至于. 那猜测, 可能是因为`decoration`没有命中同一个区域. 所以没能采用到那个较大的size?

## 批量处理当前行, 去除装饰器的效果
本来像统一用

```
	const delDecorationIfCurrentLine = (node, decoration, start=0, end=0, ...others) => {
		// console.log("decoration: ", decoration, "others:", others);

		if (node.position.start.line - 1 == editor.selection.active.line) {
			delDecoration(state, decoration, editor.selection.active.line);
		} else {
			if (others.length > 0){
				addDecoration(decoration(...others), start, end);
			} else {
				addDecoration(decoration, start, end);
			}
		}
	}
```

但是遇到一个问题, 居然有的`node`没有`position`属性...

* table
* latex
* img link

## f5调试显示的效果, 和本地打包安装后不同.

不对, `1.0.17`版本正常, 之后的版本和现在开发的版本都有问题.

`1.0.18`版本是否正常, 代表了是否我这个修改的思路是正确的...



# todo

todo: 第一级有序列表无法被`verified`库解析出`ordered`的`list`属性. 所以这种得翻一下`unified`的API, 他的判断逻辑里, 如果只有一层, 那还具有列表属性吗? listItem应该也有区分前缀才对?

todo: 遍历一层下述节点时, 第一级的`node`中包含了其内的子节点的属性. 然后会再次遍历其中的子节点. 所以这里会存在一个覆盖的效果. 目前来看只有`text`层级的`position`属性可以作为一个表来判定节点之间的关联.

todo: 下属节点的遍历能力是否要进行区分? 可能没办法区分, 因为只有遍历进`paragraph`层之后才能知道其children是否是`list`还是`listItem`.

* todo: 如果我模拟的有序列表的数字并不连续, 是否还能判定为有序列表? 得看下unified代码. 如果这里可以让直接根据在每个node的属性那里就能区分出是`ordered`与否, 那就不用考虑状态机转移了. emm, 似乎根据现有代码, 可以直接利用正则手动处理. 虽然性能低一点.
    * todo: 这里出现一个新问题, node的`value`里只有去掉了列表之后的内容, 现在导致我无法正则判断了. 怎么才能从解析后的`node`反得到对应的完整行呢? 虽然有`range`可以手动找到.
    * Todo: 我似乎可以找到对应的level层级, 手动得到前面的地址, 然后通过`range`提取到值


根据上面的`spec`可知`有序列表的开始数字由第一个列表项的数字决定，而不考虑 后面的列表项。`  所以理论上`remark`应该直接解析出`list`的`ordered`属性才对?

`remark-parse`主要用的[syntax\-tree/mdast: Markdown Abstract Syntax Tree format](https://github.com/syntax-tree/mdast#list)这个库来进行的解析.

`mdast`这个库里只是文档? 那`Remark`这么多`repo`之间的关系到底是什么?

`unified`代码里没搜到`listItem`,

重新推一下

```

const parser = require('unified')()
    .use(require('remark-math'))
    .use(require('remark-parse'))
    .use(require('remark-gfm'))
    .parse;
```
所以应该在`remark-parse`或者`remark-gfm`里. emm, `remark-gfm`下载下来和`mdast`一样是空的...


`unified.js`和`remark.js`是什么关联? 如果单纯只是API聚合的话, 应该不值得赞助吧?

噢, 根据这篇[An Introduction to Unified and Remark \- Braincoke \| Security Blog](https://braincoke.fr/blog/2020/03/an-introduction-to-unified-and-remark/#syntax-trees), `remark`看起来更像是`unifed`的下属子集能力.
```
import {fromMarkdown} from 'mdast-util-from-markdown'
```
根据这个, 而这个代码里又写来自于`micromark`, 所以说明这个数据来源是这个库.

的确在这个库的代码里搜到了`listItem`.

根据`micromark`里的描述

> remark is the most popular markdown parser. It’s built on top of micromark and boasts syntax trees. For an analogy, it’s like if Babel, ESLint, and more, were one project.

不过似乎语法树的部分解析可能还是在其他的代码里的.

乍看, 核心逻辑都在对应的`compile`里的`handler`那里.


`micromark`输出的是`html`, 那之前那些节点信息, 是哪个插件的呢?

奇怪, 用`remark-parse`输出的节点结构基本对应上了

```
{
    "type": "root",
    "children": [
        {
            "type": "list",
            "ordered": true,
            "start": 1,
            "spread": false,
            "children": [
                {
                    "type": "listItem",
                    "spread": false,
                    "checked": null,
                    "children": [
                        {
                            "type": "paragraph",
                            "children": [
                                {
                                    "type": "text",
                                    "value": "1",
                                    "position": {
                                        "start": {
                                            "line": 1,
                                            "column": 4,
                                            "offset": 3
                                        },
                                        "end": {
                                            "line": 1,
                                            "column": 5,
                                            "offset": 4
                                        }
                                    }
                                }
                            ],
                            "position": {
                                "start": {
                                    "line": 1,
                                    "column": 4,
                                    "offset": 3
                                },
                                "end": {
                                    "line": 1,
                                    "column": 5,
                                    "offset": 4
                                }
                            }
                        }
                    ],
                    "position": {
                        "start": {
                            "line": 1,
                            "column": 1,
                            "offset": 0
                        },
                        "end": {
                            "line": 1,
                            "column": 5,
                            "offset": 4
                        }
                    }
                },
                {
                    "type": "listItem",
                    "spread": false,
                    "checked": null,
                    "children": [
                        {
                            "type": "paragraph",
                            "children": [
                                {
                                    "type": "text",
                                    "value": "2",
                                    "position": {
                                        "start": {
                                            "line": 2,
                                            "column": 4,
                                            "offset": 8
                                        },
                                        "end": {
                                            "line": 2,
                                            "column": 5,
                                            "offset": 9
                                        }
                                    }
                                }
                            ],
                            "position": {
                                "start": {
                                    "line": 2,
                                    "column": 4,
                                    "offset": 8
                                },
                                "end": {
                                    "line": 2,
                                    "column": 5,
                                    "offset": 9
                                }
                            }
                        }
                    ],
                    "position": {
                        "start": {
                            "line": 2,
                            "column": 1,
                            "offset": 5
                        },
                        "end": {
                            "line": 2,
                            "column": 5,
                            "offset": 9
                        }
                    }
                },
                {
                    "type": "listItem",
                    "spread": false,
                    "checked": null,
                    "children": [
                        {
                            "type": "paragraph",
                            "children": [
                                {
                                    "type": "text",
                                    "value": "3",
                                    "position": {
                                        "start": {
                                            "line": 3,
                                            "column": 4,
                                            "offset": 13
                                        },
                                        "end": {
                                            "line": 3,
                                            "column": 5,
                                            "offset": 14
                                        }
                                    }
                                }
                            ],
                            "position": {
                                "start": {
                                    "line": 3,
                                    "column": 4,
                                    "offset": 13
                                },
                                "end": {
                                    "line": 3,
                                    "column": 5,
                                    "offset": 14
                                }
                            }
                        }
                    ],
                    "position": {
                        "start": {
                            "line": 3,
                            "column": 1,
                            "offset": 10
                        },
                        "end": {
                            "line": 3,
                            "column": 5,
                            "offset": 14
                        }
                    }
                }
            ],
            "position": {
                "start": {
                    "line": 1,
                    "column": 1,
                    "offset": 0
                },
                "end": {
                    "line": 3,
                    "column": 5,
                    "offset": 14
                }
            }
        }
    ],
    "position": {
        "start": {
            "line": 1,
            "column": 1,
            "offset": 0
        },
        "end": {
            "line": 5,
            "column": 1,
            "offset": 16
        }
    }
}

```

好像跟`html`的结构一样, 先是外部结构, `ul`还是`ol`, 然后才是内部的item渲染.

这样的话, 也得按照`html`的逻辑去渲染, 才能区分有序列表和无序列表了把.

现阶段的实现上, 是按照`node`迭代去渲染的, 所以这块当进入子节点的时候就没办法感知了.

这样的话, 最好是找到内部节点, 然后往上去遍历节点是什么结构, 然后再渲染?

那这样的话, 最好渲染一次就不是渲染一个节点, 而是一组节点的. 这样就可以在`ordered`变量存在的那层处理了.

当节点是`listItem`类型的时候, 这里存一下父节点的信息, 是不是`list`,然后`type`为`list`的`ordered`参数作为渲染用参数.


最好是在得到这个`node`信息的时候, 就遍历一下, 然后把这个属性给加到`listItem`那项里.

接下来就是在什么遍历的时候增加这个属性了.

应该哪种都行. 反正只要type匹配即可. 增加在Visit那里了

### 作废的折叠代码.
```
	// context.subscriptions.push(vscode.languages.registerFoldingRangeProvider('markdown', {
	// 	provideFoldingRanges: (document, context, _) => {
	// 	console.log(document.languageId);
	// 	console.log("try to folding range");
	// 	let ranges = []s
	// 	const temp = new vscode.FoldingRange(1, 50, vscode.FoldingRangeKind.Comment);
	// 	ranges.push(temp);
	// 	return ranges
	// }}));
	// vscode.commands.executeCommand('editor.fold', {"selectionLines": [1]});
```

### todo: 回车和backspace按键卡顿, 怀疑跟这个`markless`的实时渲染有关. 好像禁用了markless还是卡, 开了进程监控, 也没看到是哪个进程的cpu显著的高, 除了main窗口.


## todo: `markless`是如何隐藏一部分文字的? 但是实际好像又能被搜索到? 透明色?





# 数据记录

在每个大节点的访问之后, 会再进到children内进行子节点的访问.

## 无序列表下无序列表
``` json
{
    "type": "listItem",
    "spread": false,
    "checked": null,
    "children": [
        {
            "type": "paragraph",
            "children": [
                {
                    "type": "text",
                    "value": "b",
                    "position": {
                        "start": {
                            "line": 4,
                            "column": 3,
                            "offset": 13
                        },
                        "end": {
                            "line": 4,
                            "column": 4,
                            "offset": 14
                        }
                    }
                }
            ],
            "position": {
                "start": {
                    "line": 4,
                    "column": 3,
                    "offset": 13
                },
                "end": {
                    "line": 4,
                    "column": 4,
                    "offset": 14
                }
            }
        },
        {
            "type": "list",
            "ordered": false,
            "start": null,
            "spread": false,
            "children": [
                {
                    "type": "listItem",
                    "spread": false,
                    "checked": null,
                    "children": [
                        {
                            "type": "paragraph",
                            "children": [
                                {
                                    "type": "text",
                                    "value": "b.a",
                                    "position": {
                                        "start": {
                                            "line": 5,
                                            "column": 5,
                                            "offset": 19
                                        },
                                        "end": {
                                            "line": 5,
                                            "column": 8,
                                            "offset": 22
                                        }
                                    }
                                }
                            ],
                            "position": {
                                "start": {
                                    "line": 5,
                                    "column": 5,
                                    "offset": 19
                                },
                                "end": {
                                    "line": 5,
                                    "column": 8,
                                    "offset": 22
                                }
                            }
                        }
                    ],
                    "position": {
                        "start": {
                            "line": 5,
                            "column": 3,
                            "offset": 17
                        },
                        "end": {
                            "line": 5,
                            "column": 8,
                            "offset": 22
                        }
                    }
                },
                {
                    "type": "listItem",
                    "spread": false,
                    "checked": null,
                    "children": [
                        {
                            "type": "paragraph",
                            "children": [
                                {
                                    "type": "text",
                                    "value": "b.b",
                                    "position": {
                                        "start": {
                                            "line": 6,
                                            "column": 5,
                                            "offset": 27
                                        },
                                        "end": {
                                            "line": 6,
                                            "column": 8,
                                            "offset": 30
                                        }
                                    }
                                }
                            ],
                            "position": {
                                "start": {
                                    "line": 6,
                                    "column": 5,
                                    "offset": 27
                                },
                                "end": {
                                    "line": 6,
                                    "column": 8,
                                    "offset": 30
                                }
                            }
                        }
                    ],
                    "position": {
                        "start": {
                            "line": 6,
                            "column": 3,
                            "offset": 25
                        },
                        "end": {
                            "line": 6,
                            "column": 8,
                            "offset": 30
                        }
                    }
                },
                {
                    "type": "listItem",
                    "spread": false,
                    "checked": null,
                    "children": [
                        {
                            "type": "paragraph",
                            "children": [
                                {
                                    "type": "text",
                                    "value": "b.c",
                                    "position": {
                                        "start": {
                                            "line": 7,
                                            "column": 5,
                                            "offset": 35
                                        },
                                        "end": {
                                            "line": 7,
                                            "column": 8,
                                            "offset": 38
                                        }
                                    }
                                }
                            ],
                            "position": {
                                "start": {
                                    "line": 7,
                                    "column": 5,
                                    "offset": 35
                                },
                                "end": {
                                    "line": 7,
                                    "column": 8,
                                    "offset": 38
                                }
                            }
                        }
                    ],
                    "position": {
                        "start": {
                            "line": 7,
                            "column": 3,
                            "offset": 33
                        },
                        "end": {
                            "line": 7,
                            "column": 8,
                            "offset": 38
                        }
                    }
                }
            ],
            "position": {
                "start": {
                    "line": 5,
                    "column": 3,
                    "offset": 17
                },
                "end": {
                    "line": 7,
                    "column": 8,
                    "offset": 38
                }
            }
        }
    ],
    "position": {
        "start": {
            "line": 4,
            "column": 1,
            "offset": 11
        },
        "end": {
            "line": 7,
            "column": 8,
            "offset": 38
        }
    }
}

```
## 无序列表下有序列表

``` json
{
    "type": "listItem",
    "spread": false,
    "checked": null,
    "children": [
        {
            "type": "paragraph",
            "children": [
                {
                    "type": "text",
                    "value": "o.1",
                    "position": {
                        "start": {
                            "line": 17,
                            "column": 3,
                            "offset": 93
                        },
                        "end": {
                            "line": 17,
                            "column": 6,
                            "offset": 96
                        }
                    }
                }
            ],
            "position": {
                "start": {
                    "line": 17,
                    "column": 3,
                    "offset": 93
                },
                "end": {
                    "line": 17,
                    "column": 6,
                    "offset": 96
                }
            }
        },
        {
            "type": "list",
            "ordered": true,
            "start": 1,
            "spread": false,
            "children": [
                {
                    "type": "listItem",
                    "spread": false,
                    "checked": null,
                    "children": [
                        {
                            "type": "paragraph",
                            "children": [
                                {
                                    "type": "text",
                                    "value": "o.1.1",
                                    "position": {
                                        "start": {
                                            "line": 18,
                                            "column": 6,
                                            "offset": 102
                                        },
                                        "end": {
                                            "line": 18,
                                            "column": 11,
                                            "offset": 107
                                        }
                                    }
                                }
                            ],
                            "position": {
                                "start": {
                                    "line": 18,
                                    "column": 6,
                                    "offset": 102
                                },
                                "end": {
                                    "line": 18,
                                    "column": 11,
                                    "offset": 107
                                }
                            }
                        }
                    ],
                    "position": {
                        "start": {
                            "line": 18,
                            "column": 3,
                            "offset": 99
                        },
                        "end": {
                            "line": 18,
                            "column": 11,
                            "offset": 107
                        }
                    }
                },
                {
                    "type": "listItem",
                    "spread": false,
                    "checked": null,
                    "children": [
                        {
                            "type": "paragraph",
                            "children": [
                                {
                                    "type": "text",
                                    "value": "o.1.2",
                                    "position": {
                                        "start": {
                                            "line": 19,
                                            "column": 6,
                                            "offset": 113
                                        },
                                        "end": {
                                            "line": 19,
                                            "column": 11,
                                            "offset": 118
                                        }
                                    }
                                }
                            ],
                            "position": {
                                "start": {
                                    "line": 19,
                                    "column": 6,
                                    "offset": 113
                                },
                                "end": {
                                    "line": 19,
                                    "column": 11,
                                    "offset": 118
                                }
                            }
                        }
                    ],
                    "position": {
                        "start": {
                            "line": 19,
                            "column": 3,
                            "offset": 110
                        },
                        "end": {
                            "line": 19,
                            "column": 11,
                            "offset": 118
                        }
                    }
                },
                {
                    "type": "listItem",
                    "spread": false,
                    "checked": null,
                    "children": [
                        {
                            "type": "paragraph",
                            "children": [
                                {
                                    "type": "text",
                                    "value": "o.1.3",
                                    "position": {
                                        "start": {
                                            "line": 20,
                                            "column": 6,
                                            "offset": 124
                                        },
                                        "end": {
                                            "line": 20,
                                            "column": 11,
                                            "offset": 129
                                        }
                                    }
                                }
                            ],
                            "position": {
                                "start": {
                                    "line": 20,
                                    "column": 6,
                                    "offset": 124
                                },
                                "end": {
                                    "line": 20,
                                    "column": 11,
                                    "offset": 129
                                }
                            }
                        }
                    ],
                    "position": {
                        "start": {
                            "line": 20,
                            "column": 3,
                            "offset": 121
                        },
                        "end": {
                            "line": 20,
                            "column": 11,
                            "offset": 129
                        }
                    }
                }
            ],
            "position": {
                "start": {
                    "line": 18,
                    "column": 3,
                    "offset": 99
                },
                "end": {
                    "line": 20,
                    "column": 11,
                    "offset": 129
                }
            }
        }
    ],
    "position": {
        "start": {
            "line": 17,
            "column": 1,
            "offset": 91
        },
        "end": {
            "line": 20,
            "column": 11,
            "offset": 129
        }
    }
}
```

## 有序列表下有序列表
``` json
{
    "type": "listItem",
    "spread": false,
    "checked": null,
    "children": [
        {
            "type": "paragraph",
            "children": [
                {
                    "type": "text",
                    "value": "4",
                    "position": {
                        "start": {
                            "line": 12,
                            "column": 4,
                            "offset": 58
                        },
                        "end": {
                            "line": 12,
                            "column": 5,
                            "offset": 59
                        }
                    }
                }
            ],
            "position": {
                "start": {
                    "line": 12,
                    "column": 4,
                    "offset": 58
                },
                "end": {
                    "line": 12,
                    "column": 5,
                    "offset": 59
                }
            }
        },
        {
            "type": "list",
            "ordered": true,
            "start": 1,
            "spread": false,
            "children": [
                {
                    "type": "listItem",
                    "spread": false,
                    "checked": null,
                    "children": [
                        {
                            "type": "paragraph",
                            "children": [
                                {
                                    "type": "text",
                                    "value": "4.1",
                                    "position": {
                                        "start": {
                                            "line": 13,
                                            "column": 7,
                                            "offset": 66
                                        },
                                        "end": {
                                            "line": 13,
                                            "column": 10,
                                            "offset": 69
                                        }
                                    }
                                }
                            ],
                            "position": {
                                "start": {
                                    "line": 13,
                                    "column": 7,
                                    "offset": 66
                                },
                                "end": {
                                    "line": 13,
                                    "column": 10,
                                    "offset": 69
                                }
                            }
                        }
                    ],
                    "position": {
                        "start": {
                            "line": 13,
                            "column": 4,
                            "offset": 63
                        },
                        "end": {
                            "line": 13,
                            "column": 10,
                            "offset": 69
                        }
                    }
                },
                {
                    "type": "listItem",
                    "spread": false,
                    "checked": null,
                    "children": [
                        {
                            "type": "paragraph",
                            "children": [
                                {
                                    "type": "text",
                                    "value": "4.2",
                                    "position": {
                                        "start": {
                                            "line": 14,
                                            "column": 7,
                                            "offset": 76
                                        },
                                        "end": {
                                            "line": 14,
                                            "column": 10,
                                            "offset": 79
                                        }
                                    }
                                }
                            ],
                            "position": {
                                "start": {
                                    "line": 14,
                                    "column": 7,
                                    "offset": 76
                                },
                                "end": {
                                    "line": 14,
                                    "column": 10,
                                    "offset": 79
                                }
                            }
                        }
                    ],
                    "position": {
                        "start": {
                            "line": 14,
                            "column": 4,
                            "offset": 73
                        },
                        "end": {
                            "line": 14,
                            "column": 10,
                            "offset": 79
                        }
                    }
                },
                {
                    "type": "listItem",
                    "spread": false,
                    "checked": null,
                    "children": [
                        {
                            "type": "paragraph",
                            "children": [
                                {
                                    "type": "text",
                                    "value": "4.3",
                                    "position": {
                                        "start": {
                                            "line": 15,
                                            "column": 7,
                                            "offset": 86
                                        },
                                        "end": {
                                            "line": 15,
                                            "column": 10,
                                            "offset": 89
                                        }
                                    }
                                }
                            ],
                            "position": {
                                "start": {
                                    "line": 15,
                                    "column": 7,
                                    "offset": 86
                                },
                                "end": {
                                    "line": 15,
                                    "column": 10,
                                    "offset": 89
                                }
                            }
                        }
                    ],
                    "position": {
                        "start": {
                            "line": 15,
                            "column": 4,
                            "offset": 83
                        },
                        "end": {
                            "line": 15,
                            "column": 10,
                            "offset": 89
                        }
                    }
                }
            ],
            "position": {
                "start": {
                    "line": 13,
                    "column": 4,
                    "offset": 63
                },
                "end": {
                    "line": 15,
                    "column": 10,
                    "offset": 89
                }
            }
        }
    ],
    "position": {
        "start": {
            "line": 12,
            "column": 1,
            "offset": 55
        },
        "end": {
            "line": 15,
            "column": 10,
            "offset": 89
        }
    }
}
```

## 有序列表下无序列表下有序列表
``` json
{
    "type": "listItem",
    "spread": false,
    "checked": null,
    "children": [
        {
            "type": "paragraph",
            "children": [
                {
                    "type": "text",
                    "value": "p.1",
                    "position": {
                        "start": {
                            "line": 22,
                            "column": 3,
                            "offset": 133
                        },
                        "end": {
                            "line": 22,
                            "column": 6,
                            "offset": 136
                        }
                    }
                }
            ],
            "position": {
                "start": {
                    "line": 22,
                    "column": 3,
                    "offset": 133
                },
                "end": {
                    "line": 22,
                    "column": 6,
                    "offset": 136
                }
            }
        },
        {
            "type": "list",
            "ordered": true,
            "start": 1,
            "spread": false,
            "children": [
                {
                    "type": "listItem",
                    "spread": false,
                    "checked": null,
                    "children": [
                        {
                            "type": "paragraph",
                            "children": [
                                {
                                    "type": "text",
                                    "value": "p.1.1",
                                    "position": {
                                        "start": {
                                            "line": 23,
                                            "column": 6,
                                            "offset": 142
                                        },
                                        "end": {
                                            "line": 23,
                                            "column": 11,
                                            "offset": 147
                                        }
                                    }
                                }
                            ],
                            "position": {
                                "start": {
                                    "line": 23,
                                    "column": 6,
                                    "offset": 142
                                },
                                "end": {
                                    "line": 23,
                                    "column": 11,
                                    "offset": 147
                                }
                            }
                        }
                    ],
                    "position": {
                        "start": {
                            "line": 23,
                            "column": 3,
                            "offset": 139
                        },
                        "end": {
                            "line": 23,
                            "column": 11,
                            "offset": 147
                        }
                    }
                },
                {
                    "type": "listItem",
                    "spread": false,
                    "checked": null,
                    "children": [
                        {
                            "type": "paragraph",
                            "children": [
                                {
                                    "type": "text",
                                    "value": "p.1.1.1",
                                    "position": {
                                        "start": {
                                            "line": 24,
                                            "column": 8,
                                            "offset": 155
                                        },
                                        "end": {
                                            "line": 24,
                                            "column": 15,
                                            "offset": 162
                                        }
                                    }
                                }
                            ],
                            "position": {
                                "start": {
                                    "line": 24,
                                    "column": 8,
                                    "offset": 155
                                },
                                "end": {
                                    "line": 24,
                                    "column": 15,
                                    "offset": 162
                                }
                            }
                        }
                    ],
                    "position": {
                        "start": {
                            "line": 24,
                            "column": 5,
                            "offset": 152
                        },
                        "end": {
                            "line": 24,
                            "column": 15,
                            "offset": 162
                        }
                    }
                },
                {
                    "type": "listItem",
                    "spread": false,
                    "checked": null,
                    "children": [
                        {
                            "type": "paragraph",
                            "children": [
                                {
                                    "type": "text",
                                    "value": "p.1.1.2",
                                    "position": {
                                        "start": {
                                            "line": 25,
                                            "column": 8,
                                            "offset": 170
                                        },
                                        "end": {
                                            "line": 25,
                                            "column": 15,
                                            "offset": 177
                                        }
                                    }
                                }
                            ],
                            "position": {
                                "start": {
                                    "line": 25,
                                    "column": 8,
                                    "offset": 170
                                },
                                "end": {
                                    "line": 25,
                                    "column": 15,
                                    "offset": 177
                                }
                            }
                        }
                    ],
                    "position": {
                        "start": {
                            "line": 25,
                            "column": 5,
                            "offset": 167
                        },
                        "end": {
                            "line": 25,
                            "column": 15,
                            "offset": 177
                        }
                    }
                },
                {
                    "type": "listItem",
                    "spread": false,
                    "checked": null,
                    "children": [
                        {
                            "type": "paragraph",
                            "children": [
                                {
                                    "type": "text",
                                    "value": "p.1.1.3",
                                    "position": {
                                        "start": {
                                            "line": 26,
                                            "column": 8,
                                            "offset": 185
                                        },
                                        "end": {
                                            "line": 26,
                                            "column": 15,
                                            "offset": 192
                                        }
                                    }
                                }
                            ],
                            "position": {
                                "start": {
                                    "line": 26,
                                    "column": 8,
                                    "offset": 185
                                },
                                "end": {
                                    "line": 26,
                                    "column": 15,
                                    "offset": 192
                                }
                            }
                        }
                    ],
                    "position": {
                        "start": {
                            "line": 26,
                            "column": 5,
                            "offset": 182
                        },
                        "end": {
                            "line": 26,
                            "column": 15,
                            "offset": 192
                        }
                    }
                },
                {
                    "type": "listItem",
                    "spread": false,
                    "checked": null,
                    "children": [
                        {
                            "type": "paragraph",
                            "children": [
                                {
                                    "type": "text",
                                    "value": "p.1.2",
                                    "position": {
                                        "start": {
                                            "line": 27,
                                            "column": 6,
                                            "offset": 198
                                        },
                                        "end": {
                                            "line": 27,
                                            "column": 11,
                                            "offset": 203
                                        }
                                    }
                                }
                            ],
                            "position": {
                                "start": {
                                    "line": 27,
                                    "column": 6,
                                    "offset": 198
                                },
                                "end": {
                                    "line": 27,
                                    "column": 11,
                                    "offset": 203
                                }
                            }
                        }
                    ],
                    "position": {
                        "start": {
                            "line": 27,
                            "column": 3,
                            "offset": 195
                        },
                        "end": {
                            "line": 27,
                            "column": 11,
                            "offset": 203
                        }
                    }
                }
            ],
            "position": {
                "start": {
                    "line": 23,
                    "column": 3,
                    "offset": 139
                },
                "end": {
                    "line": 27,
                    "column": 11,
                    "offset": 203
                }
            }
        }
    ],
    "position": {
        "start": {
            "line": 22,
            "column": 1,
            "offset": 131
        },
        "end": {
            "line": 27,
            "column": 11,
            "offset": 203
        }
    }
}
```


# Reference
1. [CommonMark Spec](https://spec.commonmark.org/0.30/)