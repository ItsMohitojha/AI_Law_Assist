import urllib.parse
text = "## Section 22\n\n**In short:** Yes."
words = text.split(" ")
for word in words:
    print(f"Original: {repr(word)} | Encoded: {urllib.parse.quote(word)}")
