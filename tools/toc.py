"""Book structure, transcribed from the book's own table of contents (printed page numbers)."""

FRONT = [
    ("Preamble", 8),
    ("Introduction", 9),
]

SECTIONS = [
    ("Market Basics", 11, [
        ("Random Walks & Other Misconceptions", 12),
        ("What is the Market?", 13),
        ("The Market Professionals", 14),
        ("A Special Word About Market-Makers", 15),
        ("Volume – The Key to the Truth", 16),
        ("Further Understanding Volume", 18),
        ("What is Bullish & Bearish Volume", 19),
        ("Accumulation & Distribution", 20),
        ("Strong & Weak Holders", 21),
        ("Resistance & Crowd Behaviour", 23),
        ("Supply & Demand", 25),
        ("The Basics of Market Reading", 26),
        ("How to Tell if a Market is Weak or Strong", 28),
        ("How to Identify Buying & Selling", 31),
        ("How to Identify Lack of Demand", 32),
        ("Testing Supply", 34),
        ("Pushing Up Through Supply", 36),
        ("High Volume on Market Tops", 38),
        ("Effort Versus Results", 39),
        ("The Path of Least Resistance", 40),
        ("Markets can be Marked Up (or Down)", 41),
        ("Volume Surges in Related Markets", 42),
        ("Using Different Timeframes", 44),
        ("The Relationship between the Cash & Futures Price", 45),
        ("Manipulation of the Markets", 46),
    ], 48),
    ("Trends & Volume Spread Analysis", 49, [
        ("Introduction to Trends", 50),
        ("Constructing Trend Lines", 51),
        ("Bottoms & Tops", 52),
        ("Trend Scaling", 54),
        ("Why do Trend Lines Appear to Work?", 55),
        ("Using Trends to Determine Overbought and Oversold Levels", 56),
        ("Perceived Value & Trend Lines", 58),
        ("Introducing Trend Clusters", 59),
        ("Using Trend Clusters", 61),
        ("Analysing Volume Near a Trend Line", 63),
        ("Pushing Through Supply/Support Lines", 65),
        ("Absorption Volume & Lower Trend Lines", 68),
    ], 68),
    ("The Anatomy of Bull & Bear Markets", 69, [
        ("What Starts a Bull Market?", 70),
        ("The Forces of Supply & Demand Move the Markets", 72),
        ("It All Starts With a ‘Campaign’", 73),
        ("How to Recognise the Likely Market Top", 75),
        ("How to Recognise the Likely End of a Rally", 77),
        ("Up-thrusts in More Detail", 79),
        ("The Selling Climax and Professional Support", 81),
        ("The Buying Climax and Professional Selling", 83),
        ("A Buying Climax in an Individual Stock", 85),
        ("From Bear to Bull Markets", 87),
        ("Bear Markets in General", 89),
        ("What Stops a Down-Move & how will I Recognise This?", 90),
        ("How to Recognise a Market Bottom", 92),
        ("Professional Support", 94),
        ("The Shake-out", 95),
        ("Stopping Volume", 97),
        ("Falling Pressure", 98),
    ], 98),
    ("Becoming a Trader or Investor", 99, [
        ("The Dream", 100),
        ("Beware of the News", 102),
        ("You Need a System", 105),
        ("Trading Hints & Tips", 106),
        ("What are the Main Signs of Strength?", 110),
        ("What are the Main Signs of Weakness?", 111),
        ("Checklist for Going Long (Buying)", 112),
        ("Checklist for Going Short (Selling)", 114),
        ("How to Select a Stock the Easy Way", 116),
        ("Closing Comments", 119),
    ], 120),
]

# Kept out of the dropped Section 5 brochure because they are substantive.
APPENDIX = [
    ("Suggested Reading List", 138, 138),
    ("Do Not Ignore These Trading Facts!", 140, 140),
]

GLOSSARY_RANGE = (141, 180)

# Dropped: printed 121-137 (TradeGuider product brochure), 181-185 (page-number index).
DROPPED = {
    "brochure": (121, 137),
    "index": (181, 185),
}


def printed_to_pdf(p):
    """Printed page number -> 1-based PDF page index."""
    return p - 2 if p <= 138 else p - 3
