# Presidential speech across eras

A worked gallery: comparing the vocabulary of U.S. presidential speeches across
25-year eras with keyness, rank-turbulence divergence, and the allotaxonograph.

The data are compact frequency tables under `examples/data/`, built from the
public-domain [Miller Center](https://data.millercenter.org/) presidential speech
corpus (lemmatised, lowercased, punctuation stripped) bundled with
[chronowords](https://github.com/crow-intelligence/chronowords), loaded with
`keyflux.load_counts`. A light filter drops clitic fragments and transcription
markers; genuine function words stay in (they populate the lockword diagonal).

The full, executed notebook — with every figure inline — is at
[`examples/presidential_speeches.ipynb`](https://github.com/crow-intelligence/keyflux/blob/main/examples/presidential_speeches.ipynb).

## 1. The nineteenth century vs. the twenty-first

The starkest shift: formal 19th-century governmental prose against modern
televised address. Positive keywords for **2000–2024**: *job, help, today,
tonight, worker, terrorist, afghanistan, billion*. For **1825–1849**:
*appropriation, intercourse, specie, heretofore, receipt, treasury*. The
contribution panel reads first-person modern (*we, get, help, thank, americans*)
against formal 19th-century register (*which, upon, shall, duty, treaty*).

![1825–1849 vs 2000–2024](https://raw.githubusercontent.com/crow-intelligence/keyflux/main/examples/gallery/era_2000-2024_vs_1825-1849.png)

## 2. The Progressive era vs. the Cold War

**1950–1974** keywords: *vietnam, soviet, kennedy, communist, nuclear, nixon*.
**1900–1924** keywords: *railway, isthmus, philippine, hague, reclamation,
banking* — the vocabulary of the Panama Canal, imperial expansion, and early
regulation.

![1900–1924 vs 1950–1974](https://raw.githubusercontent.com/crow-intelligence/keyflux/main/examples/gallery/era_1950-1974_vs_1900-1924.png)

## 3. The Cold War vs. the modern era

A more recent, subtler shift. **2000–2024**: *afghanistan, iraqi, qaeda, virus,
ukraine, biden*. **1950–1974**: *viet, nam, communists, khrushchev, watergate,
laos, mcnamara*.

![1950–1974 vs 2000–2024](https://raw.githubusercontent.com/crow-intelligence/keyflux/main/examples/gallery/era_2000-2024_vs_1950-1974.png)

## How alpha reframes the map

`alpha` tunes what the divergence emphasises — small `alpha` surfaces churn among
rare, low-rank words; large `alpha` surfaces shifts among common, high-rank words.
The 19thC↔21stC pair at three settings (divergence rises from 0.39 to 0.54):

**alpha = 0** (logarithmic limit — rare, low-rank churn)

![alpha 0](https://raw.githubusercontent.com/crow-intelligence/keyflux/main/examples/gallery/alpha_sweep_0.png)

**alpha = 1/3** (the text default)

![alpha 1/3](https://raw.githubusercontent.com/crow-intelligence/keyflux/main/examples/gallery/alpha_sweep_0.33.png)

**alpha = 1** (emphasises common, high-rank words)

![alpha 1](https://raw.githubusercontent.com/crow-intelligence/keyflux/main/examples/gallery/alpha_sweep_1.png)

## The diamond allotaxonograph

The same comparison in the canonical Dodds (2020) **diamond** (`allotaxonometer`):
a rotated-square rank-rank histogram with iso-divergence contours and a wordshift
list. Shared function words sit on the vertical centre near the top; era-specific
and exclusive words fan out to the lower edges.

![diamond 1825–1849 vs 2000–2024](https://raw.githubusercontent.com/crow-intelligence/keyflux/main/examples/gallery/diamond_2000-2024_vs_1825-1849.png)

## Frequent words vs. keywords — two rankings of one corpus

`allotaxonometer` compares *any* two rankings, not just two corpora. Here the
**2000–2024** corpus is ranked two ways — by raw **frequency** and by **keyness**
(log-likelihood vs the 1825–1849 reference, via `RankedList.from_scores`) — and
diamonded against itself. Function words (*the, be, and, of*) top the frequency
ranking but fall out of the keyness ranking; deictic and content words (*we, you,
america, thank*) rise. Same vocabulary, reordered.

![frequency vs keyness](https://raw.githubusercontent.com/crow-intelligence/keyflux/main/examples/gallery/diamond_frequency_vs_keyness.png)

## The script

```python title="examples/presidential_speeches.py"
--8<-- "examples/presidential_speeches.py"
```
