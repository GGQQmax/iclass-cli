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

Create the `.env` file described above and install the requirements. From the repository root, register the server with Codex:

```bash
codex mcp add iclass -- "$PWD/.venv/bin/python" "$PWD/iclass_mcp_server.py"
codex mcp list
```

The repository also includes a project-scoped configuration at `.codex/config.toml`. To use it instead, update its `command` and `cwd` values to the paths for your checkout and virtual environment, then trust the project in Codex. Project-scoped configuration is loaded only for trusted projects. Tool calls prompt for approval by default.

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