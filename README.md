# Job Market Skill Analyzer

This project is a simple Flask dashboard that compares your skills with the skills required for a selected job role.

It helps you see:

- your skill match percentage
- missing skills for the role
- top in-demand skills
- salary trends by location
- recommended skills to improve next

## Features

- default role dropdown
- skill input as a comma-separated list
- visual charts for comparison and analysis
- built-in sample dataset for demo data
- easy dashboard view with job market insights

## Project files

- `app.py` – Flask app and analysis logic
- `job_market_data.csv` – sample dataset used for comparison
- `requirements.txt` – project dependencies
- `README.md` – setup and usage instructions

## 1. Install Python

Make sure Python is installed on your system.

Check:

```bash
python --version
```

If Python is not installed, install it first.

## 2. Create a virtual environment (optional but recommended)

```bash
python -m venv venv
```

Activate it:

- Windows:

```bash
venv\Scripts\activate
```

- Mac/Linux:

```bash
source venv/bin/activate
```

## 3. Install project dependencies

```bash
pip install -r requirements.txt
```

## 4. Run the app

```bash
python app.py
```

Then open this in your browser:

```text
http://127.0.0.1:5000/
```

## 5. How to use

1. Select a role from the dropdown.
2. Type your skills in the skills field.
3. Example:

```text
Python, SQL, Excel, Power BI
```

4. Click Analyze profile.
5. The dashboard shows:
   - match percentage
   - missing skills
   - demanded skills
   - salary information
   - locations with demand

## Included dataset

The project already includes a sample dataset file called `job_market_data.csv`.

If the file is missing, the app can also generate demo data automatically.

## Requirements

The project uses:

- Flask
- Gunicorn
- python-dotenv

## Notes

- The dataset is synthetic demo data for learning and project demonstration.
- It is designed to be simple, beginner-friendly, and easy to run locally.
