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

how to build to a exe
```bash
pip install -r requirements.txt
pip install windows-curses #Might need if you using windows
pip install pyinstaller
pyinstaller main.py --onefile --name iclassCLI --add-data '.env:.'
```
