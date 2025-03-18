### Summary of the Code:
The code is a web scraper that extracts job postings from multiple websites, searches for specific keywords in job descriptions, and generates an HTML file with the results. The extracted job listings are formatted with keyword highlighting (bold and red text), and the output includes job IDs, areas, and dates. 

Key functionalities:
1. **Fetching job postings** – The script asynchronously fetches job listings from given URLs.
2. **Parsing HTML** – It extracts job details such as ID, description, date, and location using BeautifulSoup.
3. **Filtering by keywords** – Only jobs containing specific keywords (e.g., "Python", "C#", "תוכנה") are included.
4. **Generating HTML output** – The extracted job details are formatted into an HTML file.
5. **Logging** – The script logs its progress to a log file.
6. **Handling pagination** – It scrapes **up to 10 pages per website**, generating multiple URLs by appending `?page=n` to the base URL.

---

### Explanation of the Async Parts:
The script makes extensive use of asynchronous programming with `asyncio` and `aiohttp` to improve efficiency when fetching multiple web pages. Here’s how:

1. **`check_keywords_in_page()`**  
   - Uses `aiohttp` to send an asynchronous HTTP request (`async with session.get(url, timeout=10)`) to fetch the webpage.
   - Awaits `response.text()` to get the HTML content without blocking execution.

2. **`generate_html()`**  
   - Calls `check_keywords_in_page()` using `await`, ensuring the function only proceeds after receiving the job data.

3. **`check_multiple_urls()`**  
   - Uses `asyncio.create_task()` to create multiple asynchronous tasks, each calling `generate_html()` for a different URL.
   - Uses `await asyncio.gather(*tasks)` to run all tasks concurrently instead of waiting for each URL sequentially.

4. **`main()`**  
   - Calls `await extractor.check_multiple_urls(...)` to start the scraping process.
   - Uses `asyncio.run(main())` to run the entire event loop.

### Why Use Async?  
Since the script makes multiple network requests, synchronous execution would make it slow (waiting for each request to finish before starting the next). By using `asyncio` and `aiohttp`, it fetches job listings concurrently, significantly reducing the overall runtime.

# EmailSender - HTML & CSS Email Sender

`EmailSender` is a Python class that sends **styled HTML emails** with embedded CSS. It reads email credentials from a `.env` file and logs all actions to `email.log`.

## 🚀 Features
- ✅ Sends **HTML emails** with embedded CSS
- ✅ Uses **`.env` file** for SMTP settings (security best practice)
- ✅ Logs all actions to `email.log` (errors & success)
- ✅ Supports **dynamic recipients, subjects, and email content**

## 📦 Installation
1. Clone this repository:
   ```sh
   git clone https://github.com/your-repo/email-sender.git
   cd email-sender
   ```
2. Install dependencies:
   ```sh
   pip install python-dotenv
   ```
### email sender ###
## ⚙️ Setup
1. **Create a `.env` file** in the project directory:
   ```ini
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   EMAIL_SENDER=your_email@gmail.com
   EMAIL_PASSWORD=your_app_password
   ```

2. **Prepare your email template files:**
   - `email_template.html`: Your HTML content
   - `styles.css`: Your CSS styles

## 🛠 Usage
```python
from email_sender import EmailSender

# Initialize the email sender
email_sender = EmailSender()

# Send an email
email_sender.send_email(
    recipient_email="receiver_email@gmail.com",
    subject="Styled HTML Email",
    html_file="email_template.html",
    css_file="styles.css"
)
```

## 📜 Logging
All email activities are logged in `email.log`, including errors and successful sends.

## ⚠️ Security Note
- Use **App Passwords** instead of your actual email password.
- Never commit `.env` files to version control.

## 📄 License
MIT License

---
Made with ❤️ by [Your Name]

