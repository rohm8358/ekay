"""Alternate binary names found on Kali / common installs."""

from __future__ import annotations

# catalog binary -> other names that satisfy shutil.which
BINARY_ALIASES: dict[str, tuple[str, ...]] = {
    "crackmapexec": ("nxc", "crackmapexec", "cme"),
    "secretsdump.py": ("impacket-secretsdump", "secretsdump.py", "secretsdump"),
    "GetNPUsers.py": ("impacket-GetNPUsers", "GetNPUsers.py", "getNPUsers.py"),
    "smbclient.py": ("impacket-smbclient", "smbclient.py"),
    "psexec.py": ("impacket-psexec", "psexec.py"),
    "ntlmrelayx.py": ("impacket-ntlmrelayx", "ntlmrelayx.py", "ntlmrelayx"),
    "bloodhound": ("bloodhound", "bloodhound-python"),
    "certipy": ("certipy", "certipy-ad"),
    "jwt_tool": ("jwt_tool", "jwt-tool", "jwt_tool.py"),
    "testssl.sh": ("testssl.sh", "testssl"),
    "zap.sh": ("zap.sh", "zap", "zaproxy"),
    "scout": ("scout", "scout.py"),
    "osrf": ("osrf", "usufy.py", "mailfy.py"),
    "kr": ("kr", "kiterunner"),
    "evilginx": ("evilginx", "evilginx2"),
    "quark": ("quark", "quark-engine"),
    "proxychains4": ("proxychains4", "proxychains"),
    "ROPgadget": ("ROPgadget", "ropgadget"),
    "one_gadget": ("one_gadget", "one-gadget"),
    "faraday-cli": ("faraday-cli", "faraday"),
    "linpeas.sh": ("linpeas.sh", "linpeas"),
    "winPEASx64.exe": ("winPEASx64.exe", "winpeas", "winPEAS.exe"),
}
