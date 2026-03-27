This used to run in powershell as Admin

Install WSL and Ubantu platforms.

1. Install the WSL2 Linux kernel

Download and install it from Microsoft:

**Download:**
[https://aka.ms/wsl2kernel](https://aka.ms/wsl2kernel)

Run the `.msi` installer.

2. set WSL2 as default

Open **PowerShell (Admin)** again and run:

``` powershell
wsl --set-default-version 2
```

3. Install Ubuntu

Open **Microsoft Store**, search for **Ubuntu**, and install it.

Or run:

```powershell
wsl --install -d Ubuntu
```
4. Start Linux

Open **Ubuntu** from the Start Menu and create your:

* Linux **username**
* Linux **password**

---

After that, open Linux anytime with:

```powershell
wsl
```

## once it instlled and setup is done . Please run following commands 

1. Update Ubuntu inside WSL

Open your **WSL Ubuntu terminal** and run:

```bash
sudo apt update
sudo apt upgrade -y

# Note : everytime we give sudo command , it ask for userid and password 

2. Then install required dependencies 

```bash
sudo apt install software-properties-common -y
```

### Now default repository may not inculde the exact python version we want . So we can use deadsnakes repository (to manage exact python version )
```
In our case we are using 3.11.15 version . To install use following commands.

```bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
```

--- to install 3.11 follow following command and run in linux platform

1. Install Python 3.11

```bash
sudo apt install python3.11 -y
```
Check the installaion using following commands 

2. ```bash
python3.11 --version
```

3. Then create a project.
```

-- mkdir my_python_project
-- cd my_python_project

4. Create a virtual environment

-- python3 -m venv venv

5. activate the virtual environmet either in linux platform or we can do this in any python application terminal.

-- source venv/bin/activate

## to create main python file in ubantu we can use follwoing command.

-- touch main.py

Note : create main file outside venv also with in the project folder.

## to run python project 

-- python main.py

## To ave dependencies i used 

-- pip freeze > requirements.txt





Steps to enable WSL and Virtual environment platform


1. dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart

2. dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
 
3. retart the PC to apply the changes



 