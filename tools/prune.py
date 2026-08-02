"""Remove promotional passages that survive inside the method chapters.

Section 5's brochure is dropped wholesale by toc.py. What is left here are the
product plugs woven into Williams' own prose. Each rule is explicit and is
checked against the text at build time — if a rule stops matching, the build
fails loudly rather than silently keeping (or losing) content.

Rule kinds
  drop      remove the whole block containing `match`
  cut       remove exactly `match` from the block, keep the rest

A `cut` is used wherever the sentence carries method content that must survive.
"""

# (chapter slug, kind, match)
RULES = [
    # --- Preamble / Introduction -------------------------------------------
    ('preamble', 'cut',
     'Our proprietary Volume Spread AnalysisTM technology is used to generate '
     'the indicators in TradeGuider™. '),
    ('introduction', 'cut',
     ' If you own the TradeGuider software, you will see that it does an '
     'excellent job of detecting these key imbalances for you, taking the hard '
     'work out of reading the markets, and enabling you to fully concentrate '
     'on your trading.'),

    # --- Section 1 ---------------------------------------------------------
    ('volume-the-key-to-the-truth', 'cut',
     ', which is the reason TradeGuider was developed in the first place. The '
     'system is capable of analysing the markets in real-time (or at the end of '
     'the day), and displaying any one of 400 indicators on the screen to show '
     'imbalances of supply and demand'),
    ('what-is-bullish-and-bearish-volume', 'cut',
     'By using the TradeGuider software, volume activity is automatically '
     'calculated and displayed on a separate indicator called the ‘Volume '
     'Thermometer’. The accuracy of this leaves you in no doubt that b'),
    ('the-basics-of-market-reading', 'cut',
     ' We recommend using the TradeGuider software, by TradeGuider Systems Ltd '
     '(www.TradeGuider.com), since using this software will give you a '
     'significant advantage over standard charting software, as you will also '
     'be able to see our proprietary VSA indicators. There are around 400 '
     'indicators built into TradeGuider, which utilise all the introductory '
     'principles in this brief book, plus the many other advanced VSA '
     'indicators that we have developed and researched over the course of the '
     'last 15 years.'),
    ('the-basics-of-market-reading', 'cut',
     ' The TradeGuider software interprets the spread size, and all other '
     'relevant information for you, so there is no need to establish anything '
     'by eye (which can be difficult at times).'),
    ('how-to-identify-lack-of-demand', 'cut',
     ' If you have the TradeGuider software, this will help you to become a '
     'better trader by teaching you how to read the markets. In time, you will '
     'become more proficient at market analysis, such that you may even decide '
     'to trade ‘blind’, to test your skills without the supply and demand '
     'indicators built into the software.'),
    ('manipulation-of-the-markets', 'cut',
     ' The TradeGuider system will be an invaluable tool in helping you to '
     'achieve this.'),

    # --- Section 3 ---------------------------------------------------------
    ('how-to-recognise-the-likely-market-top', 'cut',
     'Unless you are using the TradeGuider software in your trading, you will '
     'probably never notice this phenomenon, because when'),
    ('up-thrusts-in-more-detail', 'drop',
     'This is a beautiful chart which demonstrates the chart reading expertise '
     'built into the TradeGuider software!'),

    # --- Section 4 ---------------------------------------------------------
    ('trading-hints-and-tips', 'cut',
     ' The TradeGuider software has an excellent stock selection system.'),
    ('checklist-for-going-long-buying', 'drop',
     'If you are using TradeGuider, are there green indicators present?'),
    ('checklist-for-going-long-buying', 'cut',
     ' If you are using TradeGuider, you can turn on the ‘instant trend’ '
     'indicator (the diamonds should be green). Also look at the colour of the '
     'bars – these should also be green.'),
    ('checklist-for-going-long-buying', 'drop',
     'If you are using TradeGuider – are there red indicators close by?'),
    ('checklist-for-going-long-buying', 'cut',
     ' If you have the TradeGuider software, use the stock scanner feature to '
     'identify the strongest and weakest stocks.'),
    ('checklist-for-going-long-buying', 'drop',
     'Note: The TradeGuider software can help you with all aspects of your '
     'analysis.'),
    ('checklist-for-going-short-selling', 'drop',
     'If you are using TradeGuider, are there red indicators present?'),
    ('checklist-for-going-short-selling', 'cut',
     ' If you are using TradeGuider, you can turn on the ‘instant trend’ '
     'indicator (the diamonds should be red). Also look at the colour of the '
     'bars – these should also be red.'),
    ('checklist-for-going-short-selling', 'drop', '(For TradeGuider users:)'),
    ('checklist-for-going-short-selling', 'drop',
     'Note: The TradeGuider software can help you with all aspects of your '
     'analysis.'),
    ('closing-comments', 'cut',
     ' (although you will be much better prepared to do this if you use '
     'TradeGuider)'),
    ('closing-comments', 'drop',
     'However, if you are of an enquiring mind, your next step is to take a '
     'look at the TradeGuider software'),
    ('closing-comments', 'cut',
     ' In recognition of this, there is a huge bookstore on our website – just '
     'click the bookstore link at www.TradeGuider.com.'),

    # --- Appendix ----------------------------------------------------------
    # Closing advert on the Trading Facts page. The wrapped-heading merge folds
    # the whole blurb into one block, so this single rule removes all of it.
    ('do-not-ignore-these-trading-facts', 'drop',
     'Isn’t it time you joined the ‘smart money’?'),
]


def apply(slug, blocks):
    """Apply the rules for one chapter. Returns (blocks, hits)."""
    hits = []
    for rule_slug, kind, match in RULES:
        if rule_slug != slug:
            continue
        matched = 0
        out = []
        for b in blocks:
            text = b.get('text')
            if text and match in text:
                matched += 1
                if kind == 'drop':
                    continue
                cleaned = text.replace(match, '').strip()
                cleaned = cleaned.replace('  ', ' ')
                if cleaned:
                    b = {**b, 'text': cleaned}
                else:
                    continue
            out.append(b)
        blocks = out
        hits.append((rule_slug, kind, match, matched))
    return blocks, hits
