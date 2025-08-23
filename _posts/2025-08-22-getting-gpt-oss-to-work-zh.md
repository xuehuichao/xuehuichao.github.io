---
layout: post
title: "为什么GPT-OSS会让你的WSL2系统崩溃（以及我是怎么修好的）"
date: 2025-08-22
categories: [ai, troubleshooting, wsl2]
lang: zh
---

每次看到有新的开源模型号称能媲美GPT-4，我就忍不住兴奋。GPT-OSS就是这样——200亿参数，听起来牛得不行。

于是我照常开启我的配置：Windows 11、WSL2跑Ubuntu、Docker里面跑Ollama。拉模型，等13GB下载完，然后问个简单问题："写个2sum的Python代码。"

然后我的世界停止了。

终端直接卡死。整个系统毫无反应。只能在Windows命令行里强制`wsl --shutdown`，未保存的东西全没了。换个问题再试，还是一样。但奇怪的是，我的Qwen2.5:32b——这货*更大*——在同样环境下跑得好好的。

这到底是怎么回事？

折腾了几个小时，试各种配置，翻社区帖子，我才意识到不是我一个人遇到这破事。这是GPT-OSS和WSL2之间的根本性冲突，很多人都中招了。不过我也找到了真正管用的解法。

下面是我发现的内容。

## 先排除硬件问题

深挖之前，得先确定不是硬件不够用。我这配置应该妥妥够了：

- **显卡**：RTX 3090，24GB显存（余量充足）
- **系统**：Windows 11 + WSL2 Ubuntu，16GB内存
- **CUDA**：最新驱动，正确的GPU直通
- **环境**：带NVIDIA容器运行时的Docker

这配置跑Qwen2.5:32b（19GB的模型）轻轻松松。所以硬件肯定不是问题。

GPT-OSS模型本身看起来也没毛病：
- 200亿参数，MXFP4量化
- 13GB大小（我24GB显存轻松搞定）
- 加载时大概用14.9GB（还剩9GB呢）
- GPU满载，29层全部卸载到显卡

看起来一切正常。模型加载很快，GPU使用率也对，*理论上*应该没问题。但就是不行。

## 那我就做了每个抓狂程序员都会做的事：对比测试

我决定用完全一样的问题测试GPT-OSS和Qwen2.5:32b，看看到底哪里不同。同样环境，同样复杂度，其他都一样。

**测试命令**：`ollama run [model] "Write a simple Python function to calculate the factorial of a number"`

结果嘛...挺有意思的。

对比结果：

**GPT-OSS (20b)**：系统直接挂，终端卡死，得`wsl --shutdown`  
**Qwen2.5:32b (32b)**：运行完美，还给了完整代码和例子

等等，啥情况？*更大*的模型好好的，小的反而把系统搞崩？

挖了挖日志，找到了关键线索。GPT-OSS一直在报这个错：

```
gpu VRAM usage didn't recover within timeout seconds=5.21793737
```

你可以用这个命令检查自己的日志中是否有这个错误：
```bash
# 如果使用Docker
docker logs ollama | grep "didn't recover within timeout"

# 如果使用systemd/原生安装
journalctl -u ollama | grep "didn't recover within timeout"
```

Qwen呢？干干净净，一点毛病没有。没有超时警告，内存管理顺畅得很。

关键来了——GPT-OSS用的是MXFP4量化，Qwen用的是Q4_K Medium。GPU后端一样，CUDA一样，别的都一样。唯一的区别就是量化格式。

这让我琢磨：搞不好根本不是资源问题，而是MXFP4和WSL2的GPU直通有兼容性问题。

## 还好，不是我一个人疯了

在继续钻牛角尖之前，我先去看看有没有其他人遇到同样问题。还好，发现一堆人都中招了，顿时心理平衡了。

GitHub上好几个问题都在说同样的事：

**[问题 #8596](https://github.com/ollama/ollama/issues/8596)**：WSL2用户碰到"gpu VRAM usage didn't recover within timeout"错误。多人中招，同样环境，同样郁闷。

**[问题 #11676](https://github.com/ollama/ollama/issues/11676)**：GPT-OSS就是不好好用GPU，总是跑到CPU上去。RTX 4070-Ti、RTX 3060、RTX 3090的用户都说遇到了。

**[问题 #4427, #7654](https://github.com/ollama/ollama/issues/4427)**：各种模型都有VRAM恢复超时，规律很明显——WSL2 + Docker + 大模型 = 要出事。

看来都指向一个问题：MXFP4量化和WSL2的GPU直通就是不对付。

## 我的推测：虚拟化层在搞鬼

折腾了这么久，我觉得问题就在这：

**MXFP4量化 + WSL2 GPU直通 = 必炸无疑**

Qwen没问题是因为用的Q4_K量化，和WSL2的虚拟化层相处愉快。但GPT-OSS的MXFP4格式好像专门跟WSL2过不去，搞得VRAM恢复总失败，最后整个WSL2系统都得重启。

解决办法？绕过WSL2，直接上Windows。

## 真正管用的办法：直接装Windows版

我知道你想说啥。"但我*就喜欢*用WSL2！"兄弟，我懂。但有时候得认怂，找个能用的办法。

下面这招对我管用：

### 1. **先把模型备份了**
别跟我一样傻，忘了备份又得重新下13GB：

```bash
# 在WSL2里 - 把模型存到Windows那边
mkdir -p /mnt/c/temp/ollama-models
docker cp ollama:/root/.ollama/models /mnt/c/temp/ollama-models/

# 看看你到底有哪些模型
docker exec ollama ollama list
```

### 2. **装个Windows版Ollama**
去[ollama.com](https://ollama.com)下载Windows版，装上就行。这样就完全绕过了WSL2那套GPU直通的破玩意。

### 3. **把模型搬回来**
```cmd
# Windows命令行里 - 先确定Ollama没在跑
xcopy "C:\temp\ollama-models\models\*" "%USERPROFILE%\.ollama\models\" /E /H /Y
```

### 4. **测试GPT-OSS**
```cmd
# 应该能看到你的模型，不用重新下载
ollama list
ollama run gpt-oss:20b "Write a simple Python function to calculate the factorial of a number"
```

成了！没有系统卡死，没有终端冻结，GPT-OSS跑得顺畅得很。

### 5. **收拾残局（可选）**
确认一切都好了以后，可以把WSL2/Docker那套清理掉：
```bash
# 在WSL2里
docker stop ollama
docker rm ollama
rm -rf /mnt/c/temp/ollama-models  # 把备份删了
```

## 为啥这招真的管用

这个解决办法之所以有效，是因为我们彻底绕过了WSL2那个有问题的GPU直通层。Windows对MXFP4量化有原生支持，NVIDIA驱动直接就能处理，而WSL2的虚拟化层在GPT-OSS的内存管理上就是搞不定。

GitHub上那些遇到问题的用户都说这招管用，说实话我用到现在一直很稳。再也没有系统卡死，再也没有丢工作，GPT-OSS想怎么跑就怎么跑。

## 总结一下

这个解决方案完美吗？谈不上。我也希望WSL2里一切都能正常工作。但有时候得实用主义一点。Windows版给你带来的是：

- GPT-OSS跑得稳
- Windows和WSL2都能用
- 系统不会崩
- 原来的模型都还在

说真的，经历过那些系统挂死之后，我宁要一个能用的方案，也不要一个看起来优雅的方案。

如果你也被GPT-OSS + WSL2搞得头疼，试试这个办法。你的神经会感谢你的。