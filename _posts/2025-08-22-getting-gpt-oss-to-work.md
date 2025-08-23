---
layout: post
title: "Why GPT-OSS Crashes Your WSL2 System (And How I Fixed It)"
date: 2025-08-22
categories: [ai, troubleshooting, wsl2]
---

I cannot help but to get excited whenever I discover a new open-source model that promises GPT-4 level performance. GPT-OSS was one of those moments - a 20-billion parameter model that seemed too good to be true.

So I fired up my usual setup: Windows 11, WSL2 with Ubuntu, Docker running Ollama. I pulled the model, waited for that 13GB download, and asked it something simple: "write the python code for 2sum."

And then my world stopped.

My terminals froze. My system became completely unresponsive. The only way out? A hard `wsl --shutdown` from Windows Command Prompt, losing any unsaved work in the process. I tried again with a different prompt. Same result. Meanwhile, my Qwen2.5:32b model - which is *larger* - works flawlessly in the exact same environment.

What is going on here?

After hours of digging, testing different configurations, and diving deep into community reports, I realized this isn't just my problem. It's a fundamental incompatibility between GPT-OSS and WSL2 that affects many users. But I also found a solution that actually works.

Here's what I discovered.

## First, Let Me Rule Out the Obvious Suspects

Before diving deep, I wanted to make sure this wasn't just a case of insufficient hardware. My setup should be more than capable:

- **GPU**: RTX 3090 with 24GB VRAM (plenty of headroom)
- **System**: Windows 11 + WSL2 Ubuntu with 16GB RAM
- **CUDA**: Latest drivers with proper GPU passthrough
- **Environment**: Docker with NVIDIA Container Runtime

This setup runs Qwen2.5:32b (19GB model) without breaking a sweat. So hardware isn't the issue.

The GPT-OSS model itself looks reasonable on paper:
- 20.9B parameters using MXFP4 quantization 
- 13GB storage (well within my 24GB VRAM)
- Should use ~14.9GB when loaded (still leaving 9GB free)
- Full GPU acceleration with 29/29 layers offloaded

Everything checks out. The model loads quickly, shows proper GPU utilization, and *should* work fine. But it doesn't.

## So I Did What Any Frustrated Developer Would Do: A Side-by-Side Comparison

I decided to run the exact same prompt on both GPT-OSS and Qwen2.5:32b to see what's different. Same environment, same complexity, same everything.

**Test**: `ollama run [model] "Write a simple Python function to calculate the factorial of a number"`

What I found was... enlightening.

Here's what I discovered:

**GPT-OSS (20b)**: System hangs, terminals freeze, requires `wsl --shutdown`  
**Qwen2.5:32b (32b)**: Works perfectly, delivers complete code with examples

Wait, what? The *larger* model works fine, but the smaller one crashes the system?

Digging deeper into the logs, I found the smoking gun. GPT-OSS consistently throws these warnings:

```
gpu VRAM usage didn't recover within timeout seconds=5.21793737
```

You can check your own logs for this error with:
```bash
# If using Docker
docker logs ollama | grep "didn't recover within timeout"

# If using systemd/native installation
journalctl -u ollama | grep "didn't recover within timeout"
```

Qwen? Clean as a whistle. No timeout warnings, smooth memory management throughout.

But here's the kicker - GPT-OSS uses MXFP4 quantization while Qwen uses Q4_K Medium. Same GPU backend, same CUDA, same everything else. The only real difference? The quantization format.

That got me thinking: maybe this isn't a resource issue at all. Maybe it's a compatibility issue between MXFP4 and WSL2's GPU passthrough.

## Turns Out, I'm Not Going Crazy

Before going down any more rabbit holes, I decided to check if other people were having the same issue. And boy, was I relieved to find I'm not alone.

Multiple GitHub issues describe the exact same problem:

**[Issue #8596](https://github.com/ollama/ollama/issues/8596)**: WSL2 users with NVIDIA GPUs getting "gpu VRAM usage didn't recover within timeout" errors. Multiple people, same environment, same frustration.

**[Issue #11676](https://github.com/ollama/ollama/issues/11676)**: GPT-OSS specifically falling back to CPU instead of using GPU properly. People with RTX 4070-Ti, RTX 3060, RTX 3090 all reporting the same issue.

**[Issues #4427, #7654](https://github.com/ollama/ollama/issues/4427)**: More VRAM recovery timeouts across different models, but the pattern is clear - WSL2 + Docker + large models = trouble.

The recurring theme? MXFP4 quantization seems to have problems with WSL2's GPU passthrough layer.

## My Hypothesis: It's the Virtualization Layer

After all this investigation, here's what I think is happening:

**MXFP4 quantization format + WSL2 GPU passthrough = disaster**

Qwen works fine because it uses Q4_K quantization, which plays nicely with WSL2's virtualization layer. But GPT-OSS's MXFP4 format seems to trigger systematic VRAM recovery failures that crash the entire WSL2 system.

The solution? Bypass WSL2 entirely.

## The Fix That Actually Works: Move to Windows

Look, I know what you're thinking. "But I *like* my WSL2 setup!" Trust me, I get it. But sometimes you have to admit defeat and find a workaround.

Here's what worked for me:

### 1. **Backup Your Models First** 
Don't make my mistake of re-downloading 13GB because you forgot to backup:

```bash
# In WSL2 - Save your models to Windows
mkdir -p /mnt/c/temp/ollama-models
docker cp ollama:/root/.ollama/models /mnt/c/temp/ollama-models/

# Check what you actually have
docker exec ollama ollama list
```

### 2. **Install Ollama on Windows**
Download Ollama for Windows from [ollama.com](https://ollama.com) and run the installer. This bypasses the problematic WSL2 GPU passthrough entirely.

### 3. **Restore Your Models**
```cmd
# In Windows Command Prompt - make sure Ollama app isn't running
xcopy "C:\temp\ollama-models\models\*" "%USERPROFILE%\.ollama\models\" /E /H /Y
```

### 4. **Test GPT-OSS**
```cmd
# Should show your models without re-downloading
ollama list
ollama run gpt-oss:20b "Write a simple Python function to calculate the factorial of a number"
```

And it works! No system hangs, no frozen terminals, just smooth GPT-OSS responses.

### 5. **Clean Up (Optional)**
Once you've confirmed everything works, you can clean up the WSL2/Docker setup:
```bash
# In WSL2
docker stop ollama
docker rm ollama
rm -rf /mnt/c/temp/ollama-models  # Remove backup
```

## Why This Actually Works

The fix works because we're eliminating the problematic WSL2 GPU passthrough layer entirely. Windows has native support for MXFP4 quantization through its NVIDIA drivers, while WSL2's virtualization layer seems to struggle with GPT-OSS's specific memory management patterns.

Multiple users in the GitHub issues have confirmed this approach works, and honestly? It's been rock solid for me. No more system hangs, no more lost work, just a working GPT-OSS model.

## Final Thoughts

Is this solution ideal? Not really. I'd prefer everything to work seamlessly in WSL2. But sometimes you have to be pragmatic. The Windows installation gives you:

- Stable GPT-OSS performance
- Access from both Windows and WSL2
- No system crashes
- All your existing models preserved

And honestly, after dealing with those system hangs, I'll take a working solution over an elegant one any day.

If you're facing the same GPT-OSS + WSL2 frustrations, give this approach a try. Your sanity will thank you.

