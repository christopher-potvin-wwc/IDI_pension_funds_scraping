# IDI - Scraping Pension Funds
This repository contains pythonic scrapers for the shareholding disclosures of various pension funds, to be used by <a href="https://www.inclusivedevelopment.net/" target="_blank">Inclusive Development International</a>.<br><br>


Working scrapers can all be run at once by executing the **main.py file**, or alternatively, scripts can be run one at a time from the **scripts folder**.

Once run, files will be output to the **data folder** underneath the shareholder name and date ran.

Lastly, **wip_Scrapers** contains contains works in progress, old, and un-automated scrapers.<br><br>

All python dependencies can be downloaded via <a href="https://docs.astral.sh/uv/getting-started/installation/" target="_blank">UV.</a>
Additionally, <a href="https://tesseract-ocr.github.io/tessdoc/Installation.html" target="_blank">Tesseract OCR.</a> is needed to run certain scrapers. 

To download dependencies:
1. Ensure <a href="https://www.python.org/downloads/" target="_blank">Python3</a> and a code editor are installed to your system
2. Install UV (click the link above)
3. Install tesseract OCR (click the link above and search for your operating system. If a prebuilt installer is available, it is reccomended.)

To run this project:
1. Clone this github repository in your code editor
2. In the terminal, run the command "uv sync" to download dependencies. (Make sure your working directory is set to the main repository folder.)
3. Execute the main script by typing "py main.py" into the terminal.