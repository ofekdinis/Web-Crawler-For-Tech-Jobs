from pathlib import Path
import traceback
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from typing import List, Dict
import os
import logging
from email_sender import EmailSender
from datetime import date
class HTMLJobExtractor:
    def __init__(self, logger: logging, file_name: str = "output.html"):
        self.file_name = file_name
        self.logger = logger
        self.jobs = []
    
    def is_hebrew(self, text: str) -> bool:
        """
        Check if the text contains Hebrew characters.
        """
        return any('\u0590' <= char <= '\u05FF' for char in text)

    def highlight_keywords(self, text: str, keywords: List[str]) -> str:
        """
        Highlights the keywords in the text by wrapping them with a <span> tag 
        that applies red color and bold styling.

        Args:
            text (str): The text to search for keywords in.
            keywords (List[str]): The list of keywords to highlight.

        Returns:
            str: The text with keywords highlighted in red and bold.
        """
        for keyword in keywords:
            text = text.replace(keyword, f'<span style="color:red; font-weight:bold;">{keyword}</span>')
        return text

    async def generate_html(self, url: str, keywords: List[str]):
        """
        Extracts job descriptions from the given URL, checks for the keywords, and generates an HTML file.
        Also prints the URL where jobs were found as a clickable link.
        """
        matching_jobs = await self.check_keywords_in_page(url, keywords)
        
        if matching_jobs:
            html_content = f"""
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Job Listings from {url}</title>
            </head>
            <body>
                <h1>Job Listings from URL: <a href="{url}" target="_blank">{url}</a></h1>
                <h2>Keywords: {', '.join(keywords)}</h2>
            """
            for job_id, job_data in matching_jobs.items():
                direction = 'rtl' if self.is_hebrew(job_data['description']) else 'ltr'
                highlighted_description = self.highlight_keywords(job_data['description'], keywords)
                html_content += f"""
                <div style="direction: {direction}; margin-bottom: 20px;">
                    <h3><strong>{job_data['title']}</strong></h3>
                    <h4>{job_id}</h4>
                    <h4><strong>מיקום :{job_data['area']}</strong></h4>
                    <h4><strong>תאריך :{job_data['date']}</strong></h4>
                    <p>{highlighted_description}</p>
                </div>
                """
            html_content += "</body></html>"

            self.save_html(html_content)
        else:
            self.logger.info(f"No matching jobs found in {url}")
    
    def save_styles_to_html(self):
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Job Listings</title>
            <link rel="stylesheet" href="styles.css">
        </head>
        """
        with open(self.file_name, "a", encoding="utf-8") as f:
            f.write(html_content)
        self.logger.info(f"HTML file generated: {os.path.abspath(self.file_name)}")

    def save_html(self, html_content: str):
        """
        Save the generated HTML content to a file.
        """
        with open(self.file_name, "a", encoding="utf-8") as f:
            f.write(html_content)
        self.logger.info(f"Content added to HTML file: {os.path.abspath(self.file_name)}")

    def extract_job_ids(self, soup: BeautifulSoup) -> Dict[str, Dict[str, str]]:
        """
        Extracts job IDs, descriptions, dates, and areas from the HTML.
        
        Args:
            soup (BeautifulSoup): Parsed HTML content.
        
        Returns:
            Dict[str, Dict[str, str]]: Dictionary where keys are job IDs and values are dictionaries containing
                                        job description, date, and area.
        """
        jobs = {}
        for job_div_inner in soup.find_all("div", class_="page-details job-candidate-list node node-jobs node-teaser view-mode-teaser"):
                #print(job_div_inner.get_text(strip=True)) 
                job_id = self.extract_text_or_default(job_div_inner, "div","field field-name-field-job-id field-type-serial field-label-inline clearfix")
                job_text = self.extract_text_or_default(job_div_inner, "div","row1 clearfix page-details-content content")
                job_title_element = job_div_inner.find("div", class_="collapse-job page-details-job clearfix")
                job_title=job_title_element.find("h3").text.strip()
                # Extract date and area using the helper function
                date = self.extract_text_or_default(job_div_inner, "span", "date-display-single")
                area = self.extract_text_or_default(job_div_inner, "span", "lineage-item lineage-item-level-0")
                jobs[job_id] = {
                    "description": job_text,
                    "date": date,
                    "area": area,
                    "title": job_title or "N/A"
                }
        return jobs

    def extract_text_or_default(self,job_div, tag, class_name, default="N/A"):
        """
        Helper function to extract text from a tag within job_div, or return a default value.
        
        Args:
            job_div: The parent HTML element containing the job information.
            tag: The HTML tag to search for (e.g., "span").
            class_name: The class name to find within the tag.
            default: The default value to return if the element is not found.
        
        Returns:
            The text from the tag, or the default value if the tag is not found.
        """
        element = job_div.find(tag, class_=class_name)
        return element.text.strip() if element else default
    async def check_keywords_in_page(self, url: str, keywords: List[str]) -> Dict[str, Dict[str, str]]:
        """
        Checks if a webpage contains any of the given keywords and extracts job IDs, descriptions, dates, and areas.
        
        Args:
            url (str): The URL of the webpage to check.
            keywords (List[str]): A list of keywords to search for.
        
        Returns:
            Dict[str, Dict[str, str]]: Dictionary of job IDs, descriptions, dates, and areas where keywords were found.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    response.raise_for_status()  # This will raise an error for non-2xx status codes
                    # Await response text to get HTML content
                    html_content = await response.text()  # Asynchronously get HTML content

        except aiohttp.ClientError as e:  # Catch any aiohttp-related exceptions
            self.logger.error(f"Error fetching {url}: {e}")
            return {}  # Return an empty dictionary if there's an error

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Extract job IDs, descriptions, dates, and areas
        jobs = self.extract_job_ids(soup)
        matching_jobs = {job_id: job_data for job_id, job_data in jobs.items() if any(keyword.lower() in job_data['description'].lower() for keyword in keywords)}
        
        return matching_jobs

    def generate_paged_urls(self, base_urls: List[str]) -> List[str]:
        """
        Generates URLs with pagination for each base URL.
        
        Args:
            base_urls (List[str]): List of base URLs.
        
        Returns:
            List[str]: List of URLs with pagination.
        """
        paged_urls = []
        for url in base_urls:
            paged_urls.append(url)  # First page without ?page=1
            for page in range(1, 10):  # Change 10 to the actual maximum page number if needed
                paged_urls.append(f"{url}?page={page}")
        return paged_urls

    async def check_multiple_urls(self, urls: List[str], keywords: List[str]) -> None:
        """
        Checks multiple URLs for the given keywords and generates HTML output.
        
        Args:
            urls (List[str]): List of URLs to check.
            keywords (List[str]): List of keywords to search for.
        """
        # Create a list to hold the task objects
        tasks = []
        for url in urls:
            task = asyncio.create_task(self.generate_html(url, keywords))
            tasks.append(task)

        # Wait for all tasks to complete
        await asyncio.gather(*tasks)

async def main():
    # Delete the html file if it exists 
    if os.path.exists("jobs_output.html"):
        os.remove("jobs_output.html")
    basedir = os.path.dirname(os.path.abspath(__file__))

    log_file  = os.path.join(basedir, "logs/webcrawler.log")

    # Delete the log file if it exists before setting up the logger
    if os.path.exists(log_file):
        os.remove(log_file)

    # Configure logging
    logging.basicConfig(
        filename=log_file,  # Log file name
        level=logging.INFO,  # Logging level
        format="%(asctime)s - %(levelname)s - %(message)s",  # Log format
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    base_urls = ["https://www.mcmc.org.il/he/jobs", "https://taasuka.galil-elion.org.il/he/jobs", "https://www.mwg.org.il/he/jobs", "https://www.mmk.org.il/he/jobs"]
    extractor = HTMLJobExtractor(logger=logging.getLogger(log_file), file_name="jobs_output.html")
    test_urls = extractor.generate_paged_urls(base_urls)
    #search_keywords = ["c#", ".net", "python", "developer","Pyton", "phyton", "פייתון", "תוכנה", "פיתון","Python","C#"]
    search_keywords = ["תוכנה","c#","PAYTHON", ".net", "python", "developer","Pyton", "phyton", "פייתון", "פיתון","Python","C#"]

    extractor.save_styles_to_html()
    await extractor.check_multiple_urls(test_urls, search_keywords)

# Example usage
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logging.error("An error occurred:", e)
        logging.error("Call stack:")
        logging.error(traceback.format_exc())
    print('done!')
    #send email
    print('sending email..')
    # Create EmailSender instance (logs to email.log)
    email_sender = EmailSender()

    # Send an email
    today = date.today()
    formatted_date = today.strftime("%d/%m/%Y")  # Change the format as needed
    email_sender.send_email(
        recipient_email="receiver_email@gmail.com",
        subject=f"From Ofek Dinisman Code Jobs Outputs {formatted_date}",
        html_file="jobs_output.html",
        css_file="styles.css"
    )
    print('email sent!')   
