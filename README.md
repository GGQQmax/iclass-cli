# iclass-cli

View the to-do list, submit your homework, and achieve more in your terminal!

---

## Installation

### Prerequisites

- Python 3.10 and before 3.14*
- Python venv virtual environments

## Auto download Script
```bash
bash <(curl -fsSL https://raw.githubusercontent.com/GGQQmax/iclass-cli/main/IclassCLI_setup.sh)
```
## Manually install

Git clone the project

```bash
git clone https://github.com/GGQQmax/iclass-cli.git
```

### Environment variables set up

add `.env` to the project folder

```bash
USERNAMEID="YOURSTUDENTID"
PASSWORD="YOURSSOPASSWORD"
```
Set up python virtual environments and install package

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Use with Codex

Create the `.env` file described above and install the requirements. The repository includes a project-scoped Codex configuration at `.codex/config.toml`. Set its `command` and `cwd` to the absolute paths for your clone. For example, if the repository is at `/home/you/git/iclass-cli`:

```toml
[mcp_servers.iclass]
command = "/home/you/git/iclass-cli/.venv/bin/python"
args = ["iclass_mcp_server.py"]
cwd = "/home/you/git/iclass-cli"
default_tools_approval_mode = "prompt"
```

Open the repository in the ChatGPT desktop app and trust the project when prompted. Project-scoped MCP configuration is loaded only for trusted projects. The `prompt` approval setting asks before each tool call.

The `codex mcp add` and `codex mcp list` commands are an alternative for users who have installed the separate Codex CLI; they are not commands provided by the `chatgpt` desktop-app launcher.

how to build to a exe
```bash
pip install -r requirements.txt
pip install windows-curses #Might need if you using windows
pip install pyinstaller
pyinstaller main.py --onefile --name iclassCLI --add-data '.env:.'
```

## Some pro tip
quick upload file by using grep
```bash
ls | grep "grep fillter" | iclassCLI -u
```
Or you are doing wth your are
```bash
ls | grep HWK10 | iclassCLI -u --raw | iclassCLI -s -i "$(iclassCLI --todo | awk '/HWK10/{print $NF}')" -ids -
```
I think you got the idea