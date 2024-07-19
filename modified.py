import csv
import time
import random
import traceback
from collections import Counter

import requests
from bs4 import BeautifulSoup


SCRAPERAPI_API_KEY = "86eb5fef4b83d483b3e780d6fe206b3e" # Phil Greenwood
SCRAPERAPI_API_KEY = "2d2fec209ebcf9ee34feab97ebcc9689" # Phil Greenwood
SCRAPERAPI_COUNTRY_CODE = "us"



def get_random_scraperapi_session_number():
    return random.randint(1, 999)


def get_response_from_url(url: str) -> requests.Response:
    """
    Fetches the content of a website using the Scraper API.

    This function retrieves the content from the provided URL using the Scraper API.
    The Scraper API helps bypass website restrictions and allows access to content
    that might be blocked for regular scraping attempts.

    Args:
        url (str): The URL of the website you want to fetch content from.

    Returns:
        requests.Response: The response object containing the downloaded content
        and other information from the target website.

    Raises:
        requests.exceptions.RequestException: Any exceptions that might occur during the
        HTTP request process.

    Requires:
        * `requests` library (install using `pip install requests`)
        * Scraper API account and API key (obtain from https://scraperapi.com/)
    """

    payload = {
        "api_key": SCRAPERAPI_API_KEY,
        "url": url,
        "country_code": SCRAPERAPI_COUNTRY_CODE,  # Optional
        "session_number": get_random_scraperapi_session_number(),
        "keep_headers": "true",
    }

    try:
        response = requests.get("https://api.scraperapi.com/", params=payload)
        response.raise_for_status()  # Raise an exception for unsuccessful responses (4XX or 5XX errors)
        return response
    except requests.exceptions.RequestException as e:
        raise  # Re-raise the exception for handling at the calling code


def scrape_indeed_jobs(url: str) -> list[str]:
    company_names_total = []

    while url:
        print(f"Scraping URL: {url}")

        try:
            # Send HTTP request to the URL
            response = get_response_from_url(url=url)
            response.raise_for_status()  # Raise an exception for bad response status

            # Parse the HTML content of the page with BeautifulSoup
            soup = BeautifulSoup(response.content, "html.parser")

            company_names_soup = soup.find_all("span", {"data-testid": "company-name"})

            company_names = [
                company_name_soup.text for company_name_soup in company_names_soup
            ]

            company_names_total.extend(company_names)

            # Find the next page link
            next_page_element = soup.find("a", {"aria-label": "Next Page"})
            if next_page_element:
                # Get the URL of the next page
                url = "https://www.indeed.com" + next_page_element["href"]
                print(f"Next page URL: {url}")  # Print the URL of the next page
                time.sleep(3)  # Add a delay to avoid hitting the site too frequently

            else:
                break  # Exit the loop if no more next page link found

        except requests.exceptions.RequestException as e:
            print(f"Request error: {str(e)}\n{traceback.format_exc()}")
            break  # Exit the loop on request error

    return company_names_total


def main():
    initial_url = "https://www.indeed.com/jobs?q=&l=Omaha%2C+NE&from=searchOnHP&vjk=bb061fbb5c9cb3f0"
    company_names = scrape_indeed_jobs(initial_url)

    if company_names:
        company_name_counter = Counter(company_names)

        all_company_jobs = []

        for company, opening in company_name_counter.items():
            all_company_jobs.append([company, opening])

        with open("output.csv", "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Company", "Openings"])
            writer.writerows(all_company_jobs)
        print("Scraping complete. Data written to output.csv.")
        
    else:
        print("Scraping failed. No data written.")


if __name__ == "__main__":
    main()
