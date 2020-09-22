# 第一课：python 与 vscode

## python 的介绍

Python 是由 吉多范罗苏姆（Guido van Rossum）在 1989 年圣诞期间开发的一个语言。作为 ABC 语言的一个继承。吉多希望设计个使用更轻松的编程，而作为 ABC 语言的开发者之一，ABC 语言的目的就是让语言变得“容易阅读，容易使用，容易记忆，容易学习”。

然而 ABC 语言同时存在硬件需求高，可拓展性差，易读性差等缺点。

吉多决定解决这些问题，
Python 诞生了。

![Guido van Rossum](https://i.loli.net/2020/09/07/UbtkEhN1QCLa7Yo.png)

-_吉多范罗苏姆（Guido van Rossum）_

## Python 的设计哲学

优美、清晰、简单。

Beautiful is better than ugly.
Explicit is better than implicit.
Simple is better than complex.
Complex is better than complicated.
Readability counts.

在交互模式下输入 import this 有惊喜。

## Python 的特点

Python 是一门解释型语言，需要在解释器上运行。相比编译后运行的语言，运行速度上会处于劣势。好处是跨平台简单，一处开发多处运行。

Python 是面向对象的语言，包括函数、字符串、数字甚至类型在内都是对象。适合缺少对象的同学。

Python 的第三方库丰富，因此开发极其方便，代码量极少。解决同一个问题，通常 python 的代码量只是 java 的 1/5。人生苦短，我用 python -- Bruce Eckel。

![Bruce Eckel](https://i.loli.net/2020/09/10/TYjCMRzea9QKnX1.png)

-_Bruce Eckel 是 MindView 公司的总裁，C++标准委员会拥有表决权的成员之一_

## Python 的优缺点

优点：

-   简单易学
-   免费开源
-   面向对象
-   丰富的库
-   可扩展性

缺点：

-   运行速度慢
-   代码不好管理

## Python 2 和 Python 3

Python3 是 python2 的升级版本，从设计之初便不兼容 python2。Python3 从底层架构就已经做也很大的改动的，语法上也不尽相同。

而且 python2 已在 2020 年 1 月 1 日停止维护。所以之后我们的课程以 python3 作为开发语言，而且建议手头上有 python2 学习资料的小伙伴可以把资料丢了。

## Python 的安装

可到 python 的官网https://www.python.org下载安装。
注：默认下载的 python 是 32 位，鉴于现在很多系统都已经是 64 位，安装 64 位可获得更高的性能。

Windows 3.8.5
https://www.python.org/ftp/python/3.8.5/python-3.8.5-amd64.exe

Mac 3.8.5
https://www.python.org/ftp/python/3.8.5/python-3.8.5-macosx10.9.pkg

注意勾选 Add to Path，不然会出现找不到 python 等情况。

![python 安装界面](https://i.loli.net/2020/09/10/BJINyF9sgm5hxba.png)

## 选择 vscode 作为开发工具

在 2020 年的今天，vscode 不管是使用人数、功能性、插件丰富程度都已超过 pycharm。因此我们选用 vscode 作为我们的开发工具。

![vscode](https://i.loli.net/2020/09/10/gkJyifsCKxSltM7.png)

直接到 vscode 的官网可以下载 https://code.visualstudio.com

推荐安装以下插件：

-   Python （微软针对 python 的官方插件）
-   Pylance （提供了自动导入，静态校验等功能）
-   TabNine （强大的人工智能自动补全插件）

针对 python 在 vscode 下使用的详细配置可以看这篇文章 xxxxx :TODO

## 第一行代码

首先建一个空文件夹用作项目文件夹，使用 vscode 打开。 紧接着在左侧的项目目录右键选择新建文件，取名为 first.py。

![新建](https://i.loli.net/2020/09/10/AjbOWu7Xys4zRrw.png)

激动的心，颤抖的手，写下我们的第一行代码。

```python
print('hello world')
```

点击右上角的绿色小三角运行我们的代码。

![run](https://i.loli.net/2020/09/10/Nm3uTtP2JxqpQFM.png)

如果底部出现以下内容则表明运行成功。

![content](https://i.loli.net/2020/09/10/B7JxsLpr8uOU5iK.png)

## 祝大家学有所成

第一节课的最后，有几句话要送给大家，摘自《礼记·大学》。

`古之欲明德于天下者，先治其国；欲治其国者，先齐其家；欲齐其家者，先修其身；欲修其身者，先正其心；欲正其心者，先诚其意；欲诚其意者，先致其知，致知在格物。物格而后知至，知至而后意诚，意诚而后心正，心正而后身修，身修而后家齐，家齐而后国治，国治而后天下平。`
