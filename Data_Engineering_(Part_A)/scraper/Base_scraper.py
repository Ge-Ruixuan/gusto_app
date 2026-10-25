from abc import ABC, abstractmethod
from typing import List, Dict, Any
import pandas as pd
from playwright.sync_api import sync_playwright, Page, Browser


class BaseSupermarketScraper(ABC):
    """
    Abstract Base Class for supermarket scrapers.
    Defines the standard workflow interface for fetching dynamic discount data,
    parsing HTML/API responses, and executing data cleaning pipelines.
    """

    def __init__(self, target_url: str, headless: bool = True):
        self.target_url: str = target_url
        self.headless: bool = headless

    @abstractmethod
    def extract_raw_products(self, page: Page) -> List[Dict[str, Any]]:
        """
        Extracts raw product elements (name, price string, package size string)
        from the rendered Playwright page.
        Must be implemented by chain-specific subclasses.
        """
        pass

    def run_pipeline(self) -> pd.DataFrame:
        """
        Orchestrates browser automation, raw data extraction, and normalisation.
        """
        raw_data = self._fetch_dynamic_data()
        df_cleaned = self.clean_and_normalise(raw_data)
        return df_cleaned

    def _fetch_dynamic_data(self) -> List[Dict[str, Any]]:
        """
        Launches Playwright headless browser, navigates to target URL,
        and invokes child extraction logic.
        """
        with sync_playwright() as p:
            browser: Browser = p.chromium.launch(headless=self.headless)
            page: Page = browser.new_page()
            page.goto(self.target_url, wait_until="networkidle")

            # Subclass extraction
            raw_products = self.extract_raw_products(page)

            browser.close()
            return raw_products

    def clean_and_normalise(self, raw_data: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Converts raw text dictionaries into a clean Pandas DataFrame,
        standardising price numericals, parsing package units, and computing €/kg.
        """
        if not raw_data:
            return pd.DataFrame()

        df = pd.DataFrame(raw_data)

        # Standardisation pipeline steps
        df = self._parse_prices(df)
        df = self._parse_package_sizes(df)
        df = self._compute_unit_prices(df)

        return df

    def _parse_prices(self, df: pd.DataFrame) -> pd.DataFrame:
        """Parses raw price strings (e.g., '1,49 €') into float numeric values."""
        pass

    def _parse_package_sizes(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extracts quantity numeric and unit (g, kg, ml, l) from raw size strings."""
        pass

    def _compute_unit_prices(self, df: pd.DataFrame) -> pd.DataFrame:
        """Computes uniform €/kg or €/L price for mathematical optimisation input."""
        pass