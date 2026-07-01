"""Keyness quickstart: keywords and lockwords from two raw texts.

Run with:  uv run python examples/keyness_quickstart.py
"""

from keyflux import Keyness, counts_from_text

CLIMATE_TEXT = """
The climate report warns that carbon emissions keep rising and global warming
accelerates. Climate policy must cut emissions; renewable energy and carbon
pricing are the tools. The energy transition is a climate and policy question.
"""

FINANCE_TEXT = """
The market rallied as the stock index climbed and trade volumes rose. Investors
booked profit on energy shares; the market expects more trade. Stock policy and
the global market drive profit and shares.
"""


def main() -> None:
    """Build a Keyness comparison and print keywords and lockwords."""
    focus = counts_from_text(CLIMATE_TEXT)
    reference = counts_from_text(FINANCE_TEXT)

    keyness = Keyness(
        focus,
        reference,
        measure="log_likelihood",
        min_focus_freq=1,
        min_reference_freq=1,
        reference_id="finance-text",
    )

    keywords = keyness.keywords(top=10)
    print("Positive keywords (more typical of the climate text):")
    for row in keywords.positive(5):
        print(f"  {row.type:<12} log-ratio={row.effect_size:+.2f}  {row.significance}")

    print("\nNegative keywords (more typical of the finance text):")
    for row in keywords.negative(5):
        print(f"  {row.type:<12} log-ratio={row.effect_size:+.2f}  {row.significance}")

    print("\nLockwords (stable across both texts):")
    for row in keyness.lockwords(min_freq_both=2):
        print(f"  {row.type}")

    print("\nReproducibility record:")
    for key, value in keywords.repro.to_dict().items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
