🧩 Module Status Checker

This Python script automatically monitors PCS module status values from a remote system every 15 minutes. It downloads the latest CSV export, checks each module’s status, and logs or alerts when a module’s value differs from 6 (which represents “working properly”).

🚀 Features

Runs headlessly — no browser window is shown.

Automatically logs into the system and exports the CSV file.

Detects problematic modules (value ≠ 6) and prints a clear message.

Runs continuously every 15 minutes.

⚙️ Requirements

Before running, make sure you have:

A configuration file named config_module.json in the same directory.
It must include login credentials and the target URL, for example:

{
    "auth": {
        "url": "https://example.com",
        "username": "your_username",
        "password": "your_password"
    }
}


A local directory for saving the downloaded CSV files.
Update the export_dir path inside the script to match your own folder.

🧠 Usage

Install dependencies:

pip install selenium pandas


Run the script:

python trends_status_check_no_site.py


The script will automatically check module status every 15 minutes.

🧾 Notes

Status value 6 = OK

Any other number = issue detected

The browser runs in headless mode for smooth background operation.
