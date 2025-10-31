"""
Simple utility script to count tokens in a specified text file, to get an idea of usage.
"""

from cant_be_bothered.summarization.gemini_client import GeminiClient

file_to_count = "minutes.md"

if __name__ == "__main__":
    gemini_client = GeminiClient()
    text = open(file_to_count, "r", encoding="utf-8").read()
    token_count = gemini_client.count_tokens(text)
    print(f"Token count for '{file_to_count}': {token_count}")
