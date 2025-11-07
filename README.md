# iclass-cli

View the to-do list, submit your homework, and achieve more in your terminal!

---

## Installation

### Prerequisites

- Python 3.10 and before 3.13

## Auto download Script
```bash
bash <(curl -fsSL https://raw.githubusercontent.com/GGQQmax/iclass-cli/main/IclassCLI_setup.sh)
```
## Manually install

### Environment variables set up

add `.env` to the project folder

```bash
USERNAMEID="YOURSTUDENTID"
PASSWORD="YOURSSOPASSWORD"
```

how to build to a exe

```bash
pip install -r requirements.txt
pip install pyinstaller
pyinstaller main.py --onefile --name iclassCLI --add-data '.env:.'
```

---

## UI version
```bash
pip install -r requirements.txt
pip install windows-curses #Might need if you using windows
pip install pyinstaller
pyinstaller mainUI.py --onefile --name iclassCLIUI --add-data '.env:.'
```
