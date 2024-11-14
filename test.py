import json
import time
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def header(logs):
    graphql_headers = None
    for entry in logs:
        try:
            log = json.loads(entry["message"])["message"]
            if "Network.requestWillBeSent" in log["method"] and "graphql" in log["params"]["request"]["url"]:
                graphql_headers = log["params"]["request"]["headers"]
            elif "Network.requestWillBeSentExtraInfo" in log["method"] and graphql_headers:
                extra_headers = log["params"]["headers"]
                graphql_headers.update(extra_headers)
                return graphql_headers
        except Exception as e:
            print(f"Error processing log entry: {e}")
    return graphql_headers


def capture_network_data():
    edge_options = Options()
    edge_options.add_argument("--start-maximized")
    edge_options.set_capability("ms:loggingPrefs", {"performance": "ALL"})
    service = Service(executable_path="msedgedriver.exe")  # Path to your msedgedriver
    driver = webdriver.Edge(service=service, options=edge_options)

    try:
        email = "znatiseif@gmail.com"
        password = "vGzSe@_3gNkf3az"
        login_url = "https://auth.aiesec.org/members/sign_in"

        driver.get(login_url)
        print(f"Navigated to {login_url}")

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "email"))).send_keys(email)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "password"))).send_keys(password)

        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='sign-in-button']"))).click()
        print("Sign-In button clicked")

        time.sleep(3)

        previous_url = driver.current_url
        while True:
            current_url = driver.current_url
            if current_url != previous_url:
                print(f"URL changed to {current_url}, waiting for 10 seconds...")
                time.sleep(5)
                break
            time.sleep(1)

        # Capture logs after waiting
        logs = driver.get_log("performance")
        first_graphql_headers = header(logs)

        if first_graphql_headers:
            authorization_token = first_graphql_headers.get("authorization")

            if authorization_token:
                with open("graphql_headers.json", "w", encoding="utf-8") as file:
                    json.dump(authorization_token, file)
                print("Authorization token saved to graphql_headers.json")
            else:
                print("Authorization key not found in headers.")
        else:
            print("No GraphQL request headers found.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

    finally:
        driver.quit()


capture_network_data()
