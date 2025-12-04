# Project Setup Guide

This project uses a **Python virtual environment** to isolate dependencies.  
Follow the steps below to set up and run the project on your local machine.

---

## 1. Create the Virtual Environment

Run the following command in the project root (where `requirements.txt` is located):

```bash
python -m venv env
```

This will generate a folder named `env` that contains the virtual environment.

---

## 2. Activate the Virtual Environment

### On Windows (Command Prompt):

```bash
env\Scripts\activate
```

After activation, your terminal prompt should start with:

```
(env)
```

---

## 3. Install Required Packages

With the virtual environment activated, install dependencies using:

```bash
pip install -r requirements.txt
```

This will install all packages needed for the project.

---

## 4. Deactivate the Virtual Environment (Optional)

When you're done working, run:

```bash
deactivate
```
