"""
Handles all interaction with adventofcode.com
"""

import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import requests
from bs4 import BeautifulSoup


@dataclass
class AoCPuzzle:
    year: int
    day: int
    title: str
    description_html: str
    description_text: str  # Cleaned for Claude
    input_data: str
    part2_unlocked: bool
    part2_description: Optional[str] = None


class AoCClient:
    BASE_URL = "https://adventofcode.com"
    CACHE_DIR = Path(".cache/aoc")

    def __init__(self, session_cookie: str, year: int = 2025):
        self.session = requests.Session()
        self.session.cookies.set("session", session_cookie, domain=".adventofcode.com")
        self.session.headers.update({
            "User-Agent": "advent-of-management/1.0 (github.com/yourusername/advent-of-management)"
        })
        self.year = year
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)

    def _get_cached(self, key: str) -> Optional[str]:
        """Get cached content if available."""
        cache_file = self.CACHE_DIR / f"{self.year}_{key}.txt"
        if cache_file.exists():
            return cache_file.read_text()
        return None

    def _set_cached(self, key: str, content: str) -> None:
        """Cache content for future use."""
        cache_file = self.CACHE_DIR / f"{self.year}_{key}.txt"
        cache_file.write_text(content)

    def _fetch_with_delay(self, url: str, delay: float = 1.0) -> requests.Response:
        """Fetch URL with rate limiting delay."""
        time.sleep(delay)  # Be nice to AoC servers
        response = self.session.get(url)
        response.raise_for_status()
        return response

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract puzzle title from page."""
        title_elem = soup.find("h2")
        if title_elem:
            # Title format: "--- Day X: Title ---"
            match = re.search(r"--- Day \d+: (.+) ---", title_elem.get_text())
            if match:
                return match.group(1)
        return f"Day {self.year} Puzzle"

    def _extract_description(self, soup: BeautifulSoup) -> tuple[str, str, bool, Optional[str]]:
        """
        Extract puzzle description from page.
        Returns: (html, text, part2_unlocked, part2_text)
        """
        articles = soup.find_all("article", class_="day-desc")

        if not articles:
            raise ValueError("Could not find puzzle description")

        # Part 1 is always the first article
        part1_html = str(articles[0])
        part1_text = articles[0].get_text(separator="\n", strip=True)

        # Check if Part 2 is unlocked
        part2_unlocked = len(articles) > 1
        part2_text = None

        if part2_unlocked:
            part2_text = articles[1].get_text(separator="\n", strip=True)
            # Combine for full description
            full_text = part1_text + "\n\n--- Part Two ---\n\n" + part2_text
        else:
            full_text = part1_text

        return part1_html, full_text, part2_unlocked, part2_text

    def get_puzzle(self, day: int) -> AoCPuzzle:
        """Fetch puzzle description and input for a given day."""
        # Try cache first for input (input never changes)
        cached_input = self._get_cached(f"day{day}_input")

        # Fetch puzzle page (don't cache - part 2 may unlock)
        url = f"{self.BASE_URL}/{self.year}/day/{day}"
        response = self._fetch_with_delay(url)
        soup = BeautifulSoup(response.text, "html.parser")

        title = self._extract_title(soup)
        desc_html, desc_text, part2_unlocked, part2_text = self._extract_description(soup)

        # Get input (cached or fetch)
        if cached_input:
            input_data = cached_input
        else:
            input_url = f"{self.BASE_URL}/{self.year}/day/{day}/input"
            input_response = self._fetch_with_delay(input_url)
            input_data = input_response.text
            self._set_cached(f"day{day}_input", input_data)

        return AoCPuzzle(
            year=self.year,
            day=day,
            title=title,
            description_html=desc_html,
            description_text=desc_text,
            input_data=input_data,
            part2_unlocked=part2_unlocked,
            part2_description=part2_text,
        )

    def submit_answer(self, day: int, part: int, answer: str) -> tuple[bool, str]:
        """
        Submit an answer. Returns (success, message).
        """
        url = f"{self.BASE_URL}/{self.year}/day/{day}/answer"
        data = {"level": str(part), "answer": str(answer)}

        # Longer delay before submission to be extra respectful
        time.sleep(2.0)

        response = self.session.post(url, data=data)
        response.raise_for_status()

        # Parse response to determine if correct
        soup = BeautifulSoup(response.text, "html.parser")
        main = soup.find("main")
        if not main:
            return False, "Could not parse response"

        text = main.get_text()

        if "That's the right answer" in text:
            return True, "Correct!"
        elif "That's not the right answer" in text:
            # Try to extract hint
            if "too low" in text.lower():
                return False, "Incorrect - answer is too low"
            elif "too high" in text.lower():
                return False, "Incorrect - answer is too high"
            return False, "Incorrect"
        elif "You gave an answer too recently" in text:
            # Extract wait time
            match = re.search(r"You have (\d+)m? ?(\d+)?s? left to wait", text)
            if match:
                mins = int(match.group(1)) if match.group(1) else 0
                secs = int(match.group(2)) if match.group(2) else 0
                return False, f"Rate limited - wait {mins}m {secs}s"
            return False, "Rate limited - please wait"
        elif "You don't seem to be solving the right level" in text:
            return False, "Already solved or wrong part"
        else:
            return False, f"Unknown response: {text[:200]}"

    def get_available_days(self) -> list[int]:
        """Return list of days currently available."""
        url = f"{self.BASE_URL}/{self.year}"
        response = self._fetch_with_delay(url)
        soup = BeautifulSoup(response.text, "html.parser")

        days = []
        # Look for calendar entries that are active (have links)
        for link in soup.find_all("a", class_="calendar-day"):
            href = link.get("href", "")
            match = re.search(r"/day/(\d+)", href)
            if match:
                days.append(int(match.group(1)))

        # Also check for unlocked days without special styling
        for link in soup.select("pre.calendar a"):
            href = link.get("href", "")
            match = re.search(r"/day/(\d+)", href)
            if match:
                day = int(match.group(1))
                if day not in days:
                    days.append(day)

        return sorted(days)

    def get_leaderboard_position(self, day: int) -> Optional[dict]:
        """Get personal stats for a day if available."""
        url = f"{self.BASE_URL}/{self.year}/leaderboard/self"
        response = self._fetch_with_delay(url)
        soup = BeautifulSoup(response.text, "html.parser")

        # Parse personal leaderboard (implementation depends on structure)
        # This is optional functionality
        return None
