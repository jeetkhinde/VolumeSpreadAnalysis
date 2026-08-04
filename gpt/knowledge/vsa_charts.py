"""
VSA teaching charts — drop this into Code Interpreter and call vsa_chart().

Draws bar-and-volume diagrams the way Master the Markets does: a vertical price
bar with a close tick on its right, a volume histogram underneath, and optional
highlighting and callouts.

    bars = [
        # (high, low, close, volume)  — price on any scale you like
        (46, 32, 43, 24),
        (58, 42, 55, 20),
        (64, 54, 61, 12),
    ]
    vsa_chart(bars, title="No demand",
              highlight={2: "weak"},
              notes={2: "narrow spread up-bar, low volume"},
              caption="Professionals are not taking part in the rise.")

Panels for side-by-side comparison:

    vsa_panels([
        ("A genuine test", test_bars, {1: "strong"}, "low volume — no supply left"),
        ("A failed test",  fail_bars, {1: "weak"},   "high volume — supply remains"),
    ], suptitle="A genuine test versus a failed test")
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

INK = "#23201c"
FAINT = "#8b8377"
RULE = "#d9d1c4"
PAPER = "#fbf8f3"
STRONG = "#2f6b46"
WEAK = "#9c3728"


def _draw(ax_p, ax_v, bars, highlight=None, notes=None):
    highlight = highlight or {}
    notes = notes or {}
    lows = [b[1] for b in bars]
    highs = [b[0] for b in bars]
    pad = (max(highs) - min(lows)) * 0.12 or 1
    vmax = max(b[3] for b in bars) or 1

    for i, (h, l, c, v) in enumerate(bars):
        tone = highlight.get(i)
        colour = {"strong": STRONG, "weak": WEAK}.get(tone, INK)
        lw = 3.2 if tone else 2.2

        # price bar + close tick on the right
        ax_p.plot([i, i], [l, h], color=colour, lw=lw, solid_capstyle="butt", zorder=3)
        ax_p.plot([i, i + 0.3], [c, c], color=colour, lw=lw, solid_capstyle="butt", zorder=3)

        # volume
        ax_v.bar(i, v, width=0.42,
                 color={"strong": STRONG, "weak": WEAK}.get(tone, FAINT),
                 zorder=3)

    # Callouts sit above the whole chart with a leader down to their bar, so
    # they never land on top of a neighbouring bar.
    top = max(highs) + pad * 1.9
    ax_p.set_ylim(min(lows) - pad, top)
    for i, (h, l, c, v) in enumerate(bars):
        if i in notes:
            colour = {"strong": STRONG, "weak": WEAK}.get(highlight.get(i), INK)
            ax_p.annotate(notes[i], xy=(i, h + pad * 0.12),
                          xytext=(i, top - pad * 0.35),
                          ha="center", fontsize=9, color=colour,
                          arrowprops=dict(arrowstyle="-", color=FAINT, lw=0.9))
    ax_v.set_ylim(0, vmax * 1.25)
    for ax in (ax_p, ax_v):
        ax.set_xlim(-0.7, len(bars) - 0.3)
        ax.set_xticks([])
        ax.set_yticks([])
        for s in ax.spines.values():
            s.set_visible(False)
        ax.set_facecolor(PAPER)
    ax_v.axhline(0, color=RULE, lw=1.2)
    ax_p.set_ylabel("PRICE", fontsize=8, color=FAINT, labelpad=8)
    ax_v.set_ylabel("VOL", fontsize=8, color=FAINT, labelpad=8)


def vsa_chart(bars, title="", highlight=None, notes=None, caption="", path="chart.png"):
    """One sequence of bars with a volume histogram underneath."""
    fig, (ax_p, ax_v) = plt.subplots(
        2, 1, figsize=(min(1.15 * len(bars) + 2.5, 11), 4.6),
        gridspec_kw={"height_ratios": [3, 1], "hspace": 0.12})
    fig.patch.set_facecolor(PAPER)
    _draw(ax_p, ax_v, bars, highlight, notes)
    if title:
        ax_p.set_title(title, fontsize=13, color=INK, weight="bold", pad=12)
    if caption:
        fig.text(0.5, 0.015, caption, ha="center", fontsize=9.5, color="#5b544b")
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(path, dpi=160, facecolor=PAPER)
    plt.close(fig)
    return path


def vsa_panels(panels, suptitle="", path="panels.png"):
    """panels = [(label, bars, highlight_dict, note_str), ...] side by side."""
    n = len(panels)
    fig, axes = plt.subplots(
        2, n, figsize=(3.6 * n, 4.9),
        gridspec_kw={"height_ratios": [3, 1], "hspace": 0.12, "wspace": 0.25})
    fig.patch.set_facecolor(PAPER)
    if n == 1:
        axes = axes.reshape(2, 1)

    # share one price scale so panels stay comparable
    all_bars = [b for _, bars, _, _ in panels for b in bars]
    lo = min(b[1] for b in all_bars)
    hi = max(b[0] for b in all_bars)
    pad = (hi - lo) * 0.12 or 1
    vmax = max(b[3] for b in all_bars) or 1

    for k, (label, bars, hl, note) in enumerate(panels):
        ax_p, ax_v = axes[0, k], axes[1, k]
        _draw(ax_p, ax_v, bars, hl, None)
        ax_p.set_ylim(lo - pad, hi + pad * 1.4)
        ax_v.set_ylim(0, vmax * 1.25)
        ax_p.set_title(label, fontsize=11.5, color=INK, weight="bold", pad=10)
        if k:
            ax_p.set_ylabel(""); ax_v.set_ylabel("")
    if suptitle:
        fig.suptitle(suptitle, fontsize=13.5, color=INK, weight="bold", y=0.99)
    fig.tight_layout()
    fig.subplots_adjust(bottom=0.26, top=0.88)

    # Verdicts and notes go in figure coordinates AFTER the layout pass, so the
    # layout cannot clip them.
    for k, (label, bars, hl, note) in enumerate(panels):
        box = axes[1, k].get_position()
        x = (box.x0 + box.x1) / 2
        tone = next(iter(hl.values()), None) if hl else None
        if tone:
            fig.text(x, box.y0 - 0.09, {"strong": "STRENGTH", "weak": "WEAKNESS"}[tone],
                     ha="center", fontsize=10.5, weight="bold",
                     color={"strong": STRONG, "weak": WEAK}[tone])
        if note:
            fig.text(x, box.y0 - 0.17, note, ha="center", fontsize=9.5, color="#5b544b")
    fig.savefig(path, dpi=160, facecolor=PAPER)
    plt.close(fig)
    return path
