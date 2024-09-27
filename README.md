## Features

- Scrapes job listings from Seek.com,...
- Extracts detailed information for each job posting
- Stores data in Google Sheets for easy access and analysis

## Prerequisites

- Python 3.12+
- Google Cloud project with enabled Google Sheets API
- Service account credentials for Google Sheets API

The script will scrape job listings from Seek.com,... and store the data in the specified Google Sheet.

## Project Structure

- `main.py`: Entry point of the application
- `scraping/seekcom.py`: Contains the main scraping logic
- `common/gs.py`: Handles Google Sheets operations
- `env.py`: Loads environment variables

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
