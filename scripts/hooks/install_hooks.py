#!/usr/bin/env python3
import os, stat

hook_src = os.path.join("scripts","hooks","pre-commit.sh")
hook_dst = os.path.join(".git","hooks","pre-commit")
os.makedirs(os.path.dirname(hook_dst), exist_ok=True)

with open(hook_src,"r",encoding="utf-8") as f:
    content = f.read()

with open(hook_dst,"w",encoding="utf-8") as f:
    f.write(content)

os.chmod(hook_dst, os.stat(hook_dst).st_mode | stat.S_IEXEC)
print("Installed pre-commit hook.")
