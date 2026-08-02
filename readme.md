# How to Set Up and Run the Experiment

This document explains how to set up the required Python environment and run the experiment file `benchmark_updated.py`.

The experiment is designed to run with **Python 3.11.15**. On Windows, the recommended setup is **WSL2 (Windows Subsystem for Linux 2) with Ubuntu**.

> **Note:** If WSL/Ubuntu is already installed and configured on your computer, you can skip directly to [Step 3: Set Up the Python Environment](#3-set-up-the-python-environment).

---

# 1. System Requirements

The following are required to run the experiment:

* Windows with WSL2 support
* Ubuntu running inside WSL2
* Python **3.11.15**
* `requirements.txt`
* `Symptom2Disease.csv`
* Gemini AI Studio API key
* Internet connection

The experiment file to be executed is:

```text
benchmark_updated.py
```
### How to create Gemini AI studios API ---
1. Go to following website : https://aistudio.google.com/api-keys 
2. On top right corner , we can see create new API key , copy it 
3. Now paste the API key in the benchmark_updated.py file under configuration section (line 29)
4. API key looks like -- 'AQ.Ab............UdZw'
---

# 2. Install and Configure WSL2

WSL2 allows Linux and Ubuntu to run directly on Windows. The following steps are required if WSL2 and Ubuntu are not already installed.

## 2.1 Enable WSL and Virtual Machine Platform

Open **PowerShell as Administrator** and run:

```powershell
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
```

Then run:

```powershell
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
```

Restart the computer after running these commands.

---

## 2.2 Install the WSL2 Linux Kernel

If required, download and install the WSL2 Linux kernel from Microsoft:

https://aka.ms/wsl2kernel

Run the downloaded `.msi` installer and complete the installation.

---

## 2.3 Set WSL2 as the Default Version

After restarting the computer, open **PowerShell as Administrator** and run:

```powershell
wsl --set-default-version 2
```

This ensures that newly installed Linux distributions use WSL2.

---

## 2.4 Install Ubuntu

Ubuntu can be installed through the **Microsoft Store**:

1. Open Microsoft Store.
2. Search for **Ubuntu**.
3. Install Ubuntu.

Alternatively, open PowerShell and run:

```powershell
wsl --install -d Ubuntu
```

---

## 2.5 Start Ubuntu

Open **Ubuntu** from the Windows Start Menu.

During the first launch, Ubuntu will ask you to create:

* a Linux username
* a Linux password

These credentials are used when working inside the Ubuntu/WSL environment.

You can subsequently open Ubuntu from PowerShell using:

```powershell
wsl
```

---

# 3. Set Up the Python Environment

Once Ubuntu/WSL2 is installed, open the **Ubuntu terminal**.

All commands in this section should be executed inside Ubuntu unless otherwise specified.

## 3.1 Update Ubuntu

Run:

```bash
sudo apt update
sudo apt upgrade -y
```

> **Note:** Commands using `sudo` may ask for your Ubuntu/Linux password.

---

## 3.2 Install Required System Dependencies

Install `software-properties-common`:

```bash
sudo apt install software-properties-common -y
```

---

## 3.3 Install Python 3.11

The experiment requires **Python 3.11.15**.

Ubuntu's default repositories may not contain the required Python version. Therefore, the Deadsnakes PPA can be used to install Python 3.11.

Add the repository:

```bash
sudo add-apt-repository ppa:deadsnakes/ppa
```

Then update the package list:

```bash
sudo apt update
```

Install Python 3.11:

```bash
sudo apt install python3.11 -y
```

Verify the installation:

```bash
python3.11 --version
```

The expected output should be similar to:

```text
Python 3.11.15
```

---

# 4. Create the Project Directory

Navigate to the location where you want to store the project.

For example:

```bash
mkdir rulechef_proj
cd rulechef_proj
```

The project directory should contain the experiment files, dataset, and `requirements.txt`.

For example:

```text
rulechef_proj/
├── benchmark_updated.py
├── Symptom2Disease.csv
├── requirements.txt
└── ...
```

---

# 5. Create a Python Virtual Environment

Inside the project directory, create a virtual environment:

```bash
python3.11 -m venv .venv
```

This creates a separate Python environment in the `.venv` directory.

The project will then look approximately like:

```text
rulechef_proj/
├── .venv/
├── benchmark_updated.py
├── Symptom2Disease.csv
├── requirements.txt
└── ...
```

> **Important:** The `.venv` directory is the virtual environment. It is not necessary to place your Python source files inside this directory.

---

# 6. Activate the Virtual Environment

### Ubuntu / WSL / Bash

Run:

```bash
source .venv/bin/activate
```

After activation, the terminal should show `(.venv)` at the beginning, for example:

```text
(.venv) user@computer:~/rulechef_proj$
```

### Windows PowerShell

If you are running the environment directly from Windows PowerShell instead of WSL:

```powershell
.venv\Scripts\Activate.ps1
```

### Windows Command Prompt

```cmd
.venv\Scripts\activate
```

For this experiment, **WSL/Ubuntu with Bash is recommended**.

---

# 7. Upgrade pip

Once the virtual environment is activated, upgrade `pip`:

```bash
python -m pip install --upgrade pip
```

---

# 8. Install the Required Python Packages

Make sure that `requirements.txt` is located in the project directory.

Install all required packages using:

```bash
pip install -r requirements.txt
```

This will install the Python packages required by the experiment.

You can verify the installed packages using:

```bash
pip list
```

---

# 9. Verify the Project Files

Before running the experiment, make sure the required files are available.

The project should contain at least:

```text
rulechef_proj/
│
├── .venv/
├── benchmark_updated.py
├── Symptom2Disease.csv
└── requirements.txt
```

The `.venv/` directory is created automatically when the virtual environment is created.

---

# 10. Configure the Gemini API Key

The experiment requires a **Gemini AI Studio API key**.

Make sure your API key is available to the experiment in the way expected by `benchmark_updated.py`.

For example, if the Python script reads the API key from an environment variable, set it before running the experiment:

```bash
export GEMINI_API_KEY="YOUR_API_KEY_HERE"
```

> **Security note:** Do not commit or upload your API key to GitHub or include it directly in the source code.

If the experiment uses a different environment-variable name, use the name specified in `benchmark_updated.py`.

---

# 11. Run the Experiment

After completing the setup and activating the virtual environment, run:

```bash
python benchmark_updated.py
```

The complete sequence from an already-configured Ubuntu/WSL terminal is:

```bash
cd rulechef_proj

python3.11 -m venv .venv

source .venv/bin/activate

python -m pip install --upgrade pip

pip install -r requirements.txt

python benchmark_updated.py
```

> **Important:** If the `.venv` environment has already been created, do not create it again. Simply activate it:

```bash
source .venv/bin/activate
```

and then run:

```bash
python benchmark_updated.py
```

---

# 12. Deactivate the Virtual Environment

When you have finished running the experiment, you can leave the virtual environment using:

```bash
deactivate
```

This does not delete the environment. It only exits the currently active virtual environment.

To use it again later:

```bash
cd rulechef_proj
source .venv/bin/activate
```

---

# 13. Complete Setup Summary

If WSL2, Ubuntu, and Python 3.11.15 are already installed, the following commands are sufficient to prepare and run the experiment:

```bash
cd rulechef_proj

python3.11 -m venv .venv

source .venv/bin/activate

python -m pip install --upgrade pip

pip install -r requirements.txt

python benchmark_updated.py
```

If the virtual environment already exists, use:

```bash
cd rulechef_proj
source .venv/bin/activate
python benchmark_updated.py
```

---

# 14. Troubleshooting

## Python version is incorrect

Check the Python version:

```bash
python3.11 --version
```

You should see:

```text
Python 3.11.15
```

Also check the Python version inside the virtual environment:

```bash
python --version
```

---

## `python` command is not found

Try:

```bash
python3.11 --version
```

If Python 3.11 is installed, create the environment using:

```bash
python3.11 -m venv .venv
```

---

## `pip` command is not found

Make sure the virtual environment is activated:

```bash
source .venv/bin/activate
```

Then run:

```bash
python -m pip --version
```

---

## `requirements.txt` cannot be found

Make sure you are inside the project directory:

```bash
pwd
```

Then list the files:

```bash
ls
```

You should see:

```text
benchmark_updated.py
requirements.txt
Symptom2Disease.csv
```

If `requirements.txt` is present, run:

```bash
pip install -r requirements.txt
```

---

# 15. Recommended Project Structure

The final project should approximately have the following structure:

```text
rulechef_proj/
│
├── .venv/
│   └── ...
│
├── benchmark_updated.py
├── Symptom2Disease.csv
├── requirements.txt
└── README.md
```

The `.venv/` directory contains the isolated Python environment and normally should **not** be committed to the project repository.

---

# Quick Start

For a machine where WSL2, Ubuntu, and Python 3.11.15 are already configured:

```bash
cd rulechef_proj
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python benchmark_updated.py
```

**The main experiment file is:**

```text
benchmark_updated.py
```

**Required dataset:**

```text
Symptom2Disease.csv
```

**Required dependency file:**

```text
requirements.txt
```

**Required Python version:**

```text
Python 3.11.15
```

**Required API access:**

```text
Gemini AI Studio API key
```
