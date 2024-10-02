import jdatetime
from datetime import datetime


def gregorian_to_jalali(date_str):
    """
    Convert a Gregorian date string (in the format YYYY-MM-DD H:M:S.MMMMMM) to the Jalali calendar.

    Args:
        date_str (str): A string representing the Gregorian date.

    Returns:
        str: Jalali date in the format YYYY-MM-DD.
    """
    # Parse the date string into a datetime object (including microseconds)
    gregorian_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S.%f')

    # Convert to Jalali date
    jalali_date = jdatetime.date.fromgregorian(date=gregorian_date)

    # Return formatted Jalali date
    return jalali_date.strftime('%Y-%m-%d')


from bs4 import BeautifulSoup


def extract_content_from_html(html):
    """
    Extract the textual content from an HTML string.

    Args:
        html (str): The HTML string.

    Returns:
        str: The plain text content of the HTML element.
    """
    soup = BeautifulSoup(html, 'html.parser')
    return soup.get_text(strip=True)

