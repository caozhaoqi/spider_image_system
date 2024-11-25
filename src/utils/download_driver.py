import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import subprocess
from loguru import logger
import re
import stat
import zipfile
import psutil
import requests
from lxml import etree
import time


class ChromeDriverDownloader:
    """Downloads and manages ChromeDriver that matches local Chrome version"""

    def __init__(self):
        self.chrome_drive_url = "https://chromedriver.chromium.org/downloads"
        self.headers = {
            'content-type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'
        }
        self.driver_path = Path.cwd() / "chromedriver_win32"
        self.zip_path = Path.cwd() / "chromedriver_win32.zip"

    @logger.catch
    def get_chromedriver_urls(self):
        """Get list of available ChromeDriver versions"""
        try:
            with requests.Session() as session:
                response = session.get(self.chrome_drive_url, headers=self.headers, verify=False)
                html = etree.HTML(response.text)
                version_hrefs = html.xpath(".//strong//..//@href")
                logger.debug("Available Chrome versions:")
                for href in version_hrefs:
                    logger.debug(href)
                return version_hrefs
        except Exception as e:
            logger.error(f"Failed to get ChromeDriver versions: {e}")
            return None

    @logger.catch 
    def download_chrome_drive(self, url):
        """Download ChromeDriver zip file"""
        try:
            with requests.Session() as session:
                response = session.get(url, headers=self.headers, verify=False)
                if response.status_code == 200:
                    with open(self.zip_path, "wb") as f:
                        f.write(response.content)
                    logger.debug("Download completed")
                    return True
                logger.warning(f'Request failed with status code: {response.status_code}')
                return False
        except Exception as e:
            logger.warning(f"Failed to download ChromeDriver: {e}")
            return False

    @logger.catch
    def find_matching_version(self, local_version, available_versions):
        """Find matching ChromeDriver version"""
        local_major = local_version.split(".")[0]
        for href in available_versions:
            try:
                version_match = re.search(r"path=(.*?)/", href)
                if version_match:
                    driver_major = version_match.group(1).split(".")[0]
                    if local_major == driver_major:
                        return href
            except Exception:
                continue
        logger.debug(f"No matching ChromeDriver found for Chrome {local_version}")
        return None

    @logger.catch
    def kill_chromedriver_process(self):
        """Kill any running ChromeDriver processes"""
        logger.debug("Checking for running ChromeDriver processes")
        for proc in psutil.process_iter(['name']):
            try:
                if proc.name() == "chromedriver.exe":
                    proc.kill()
                    logger.debug('Killed ChromeDriver process')
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        logger.debug('No ChromeDriver process found')
        return False

    @logger.catch
    def unzip_driver(self):
        """Extract ChromeDriver zip file"""
        self.kill_chromedriver_process()
        
        if self.driver_path.exists():
            for file in self.driver_path.iterdir():
                file.chmod(stat.S_IRWXU)
                
        time.sleep(1)
        
        with zipfile.ZipFile(self.zip_path) as zf:
            zf.extractall(self.driver_path)
            
        logger.success(f"ChromeDriver extracted to: {self.driver_path}")

    @logger.catch
    def start(self):
        """Main execution flow"""
        version = get_chrome_version()
        if not version:
            logger.error("Failed to detect Chrome version")
            return False

        logger.debug(f"Chrome version: {version}")

        version_urls = self.get_chromedriver_urls()
        if not version_urls:
            return False

        matching_url = self.find_matching_version(version, version_urls)
        if not matching_url:
            return False

        logger.debug(f"Found matching version: {matching_url}")
        
        version_num = re.search(r"path=(.*?)/", matching_url).group(1)
        base_url = matching_url.rsplit('/', 2)[0]
        download_url = f"{base_url}/{version_num}/chromedriver_win32.zip"
        
        logger.debug(f"Downloading from: {download_url}")
        
        if not self.download_chrome_drive(download_url):
            return False
            
        self.unzip_driver()
        return True


@logger.catch
def get_chrome_version():
    """Get installed Chrome version"""
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    try:
        command = f'wmic datafile where name="{chrome_path}" get Version'
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            version_lines = result.stdout.strip().split('\n\n')
            if len(version_lines) > 1:
                return version_lines[1].strip()
                
        logger.warning(f"Command failed: {result.stderr}")
    except Exception as e:
        logger.error(f"Failed to get Chrome version: {e}")
    return None
