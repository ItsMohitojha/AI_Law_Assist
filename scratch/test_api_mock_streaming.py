import urllib.parse

# 1. Simulating the backend response with exact markdown structure (headings, bold, newlines, lists)
mock_answer = """## Section 181
This section specifies the penalty for driving a motor vehicle without authorization.

**In short:** Driving a motor vehicle without a license can lead to imprisonment.

---

### What This Means
If you operate a vehicle without a **driving license**, you commit an offense.

### Key Points
- **First Point** — detail text
- **Second Point** — other text
"""

# 2. Simulating backend streaming splitting and encoding (like in api.py)
words = mock_answer.split(" ")
streamed_chunks = []
for word in words:
    if word:
        streamed_chunks.append(urllib.parse.quote(word))

# 3. Simulating frontend receiving and decoding (like in index.html)
reconstructed_full = ""
for chunk in streamed_chunks:
    decoded_word = urllib.parse.unquote(chunk)
    reconstructed_full += decoded_word + " "

print("=== MOCK ANSWER MATCH TEST ===")
print("Does reconstructed text match original (ignoring trailing space variations)?")
# Cleanup multiple spaces from original to compare
clean_original = " ".join([w for w in mock_answer.split(" ") if w])
clean_reconstructed = " ".join([w for w in reconstructed_full.split(" ") if w])
print("Match:", clean_original == clean_reconstructed)

print("\n--- RECONSTRUCTED OUTPUT ---")
print(reconstructed_full)
print("----------------------------")
