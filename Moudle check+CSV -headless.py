# trends_status_check_no_site_auto_headless.py
import json
import time
import os
import pandas as pd
import ctypes  # For Windows popup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


# ---------- helpers ----------
def load_config(path="config_module.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _click_element(driver, el):
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
    driver.execute_script("arguments[0].click();", el)


def setup_driver_headless(download_path):
    opts = Options()
    opts.add_argument("--headless=new")  # headless mode
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    prefs = {
        "download.default_directory": download_path,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    opts.add_experimental_option("prefs", prefs)
    return webdriver.Chrome(options=opts)


# ---------- CSV summary & module check ----------
def summarize_second_last_row(csv_path):
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            sample = f.read(2048)
            import csv
            dialect = csv.Sniffer().sniff(sample)

        df = pd.read_csv(csv_path, delimiter=dialect.delimiter)
        if 't_stamp' not in df.columns:
            print("❌ Could not find column 't_stamp' in CSV.")
            return

        second_last_row = df.iloc[-2]
        timestamp = second_last_row['t_stamp']
        print(f"\n🕒 Second-to-last timestamp: {timestamp}")

        for col in df.columns:
            if "module_" in col.lower():
                try:
                    pcs = "PCS01" if "pcs01" in col.lower() else "PCS02"
                    module_num = col.split("module_")[1].split("/")[0]
                    value = second_last_row[col]

                    print(f"{pcs:<6} Module {module_num}: {value}")

                    # Check if value is different from 6
                    if int(value) != 6:
                        msg = f"⚠️ Problem detected: {pcs} Module {module_num} = {value}"
                        print(msg)
                        ctypes.windll.user32.MessageBoxW(0, msg, "Module Issue", 0x40 | 0x1)

                except Exception:
                    pass

    except Exception as e:
        print("❌ Error while reading CSV:", e)


# ---------- main automation ----------
def main():
    cfg = load_config("config_module.json")
    auth = cfg["auth"]

    export_dir = "put your own dir to save the CSV file"
    os.makedirs(export_dir, exist_ok=True)

    driver = setup_driver_headless(export_dir)
    wait = WebDriverWait(driver, 20)

    try:
        driver.get(auth["url"])
        time.sleep(1)

        # Login process
        try:
            el = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[normalize-space(text())='CONTINUE TO LOG IN']")))
            _click_element(driver, el)
        except TimeoutException:
            pass

        u_el = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@name='username' or @id='username']")))
        u_el.send_keys(auth["username"])
        _click_element(driver, wait.until(EC.element_to_be_clickable((By.XPATH, "//*[normalize-space(text())='CONTINUE']"))))

        p_el = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@name='password' or @type='password']")))
        p_el.send_keys(auth["password"])
        _click_element(driver, wait.until(EC.element_to_be_clickable((By.XPATH, "//*[normalize-space(text())='CONTINUE']"))))

        time.sleep(2)

        # Navigate to Trends → Status Modules
        try:
            trends_el = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(normalize-space(.),'Trends')]")))
            _click_element(driver, trends_el)
            time.sleep(1)
            print("✅ Clicked 'Trends'")
            time.sleep(1)
        except Exception:
            print("❌ 'Trends' not found")

        try:
            status_modules_el = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(normalize-space(.),'Status Modules')]")))
            _click_element(driver, status_modules_el)
            time.sleep(1)
            print("✅ Clicked 'Status Modules'")
        except Exception:
            print("❌ 'Status Modules' not found")

        # Export CSV
        time.sleep(3)
        try:
            export_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'Export')] | //span[contains(.,'Export')]"))
            )
            _click_element(driver, export_button)
            print("✅ Clicked 'Export' — downloading CSV...")
            time.sleep(6)
        except Exception as e:
            print("❌ Couldn't click 'Export':", e)

        # Find the newest CSV file
        list_of_files = [os.path.join(export_dir, f) for f in os.listdir(export_dir) if f.lower().endswith(".csv")]
        if list_of_files:
            latest_file = max(list_of_files, key=os.path.getctime)
            print(f"\n📁 Latest CSV detected: {latest_file}")
            summarize_second_last_row(latest_file)
        else:
            print("❌ No CSV files found in folder.")

    except Exception as e:
        print("❌ Error:", e)

    finally:
        try:
            driver.quit()
        except Exception:
            pass


# ---------- run every 15 minutes ----------
if __name__ == "__main__":
    while True:
        print("\n⏱ Starting module check...")
        main()
        print("\n⏱ Waiting 15 minutes for next check...")
        time.sleep(900)  # 15 minutes

