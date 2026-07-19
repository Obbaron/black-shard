# The Black Shard: Wiki Schema

**Status:** Author's specification. Not in-universe.
**Derived from:** `religion/eutaxia.md`, the first article written to this standard.
**Applies to:** every `.md` file in the wiki.

---

## The Governing Principle

**Nothing is asserted. Everything is attested.**

Every article is written *by someone in the world*, for *someone in the world*, for *a reason*. There is no neutral narrator, and there is no view from nowhere. Before a sentence enters the wiki it must answer:

1. **Is it true?** (author-level truth: the thing that actually happened)
2. **Who knows it?** (which in-world party has access)
3. **Which document holds it?** (which file, in whose voice)

A fact with no knower **cannot appear in any article**. It either needs a source invented for it, or it stays a hole that in-world scholars can **detect but not fill**, which is itself good content.

### Consequences

- **The article body is 100% in-universe.** No hedging. No "the Eutaxians believe that..." The source *professes*.
- **The author's voice lives in HTML comments**, which are invisible when markdown renders. Nothing is lost; nothing leaks.
- **Bias is a feature.** A source with no motive to distort is not a source. It is the author wearing a hat.
- **Contradictions between articles are correct** and must not be resolved in the articles themselves. The reader assembles the truth. Nobody hands it to them.

---

## File Anatomy

Every article has four layers, in this order.

```
1. YAML frontmatter        (out-of-world; source + bias declaration)
2. Authorial note block    (out-of-world; HTML comment; the discipline for this file)
3. The article body        (100% in-world; the source professing)
4. The apparatus           (out-of-world; HTML comment; TODOs, counter-sources, analysis)
```

---

## 1. Frontmatter

Required on every article. Governs the file without appearing in it.

```yaml
---
source: The Hierophancy of Sophras
perspective: Eutaxian, orthodox. Written by the order of Sophras for the instruction of the higher clergy.
reliability: Doctrinally authoritative. Mathematically exact. Systematically silent upon the cost of the Severance, which is not held in this hand.
status: draft
---
```

| Field | Purpose |
|---|---|
| `source` | The in-world institution or individual who wrote this. |
| `perspective` | Their allegiance, their audience, their genre. |
| `reliability` | **What they are good for, and what they are blind to.** The most important field. Write it before you write the article. |
| `status` | `draft` / `stable` / `contested` |

**`reliability` is the contract.** If the article ever says something the reliability field forbids, the article is wrong, not the field.

---

## 2. The Authorial Note

An HTML comment at the top, stating the discipline for this specific file. It exists so that a future edit does not accidentally break voice.

Structure:

```markdown
<!--
    AUTHORIAL NOTE. This article is written from inside the faith. The Hierophancy
    believes every word of it. Menneus IS holy; the Severance WAS righteous.
    Nothing here may be phrased as "the Eutaxians believe." They are not
    reporting. They are professing.

    What this source CANNOT say, and must never be made to say:
      - that Monas was ever not alone
      - that the Plerosis covers a hole in the year
      - what the Severance cost

    The counter-testimony lives in ledger.md and vestrn_chronicle.md.
-->
```

**The "cannot say" list is the heart of it.** A source is defined more sharply by its silences than by its claims.

---

## 3. The Body

### Voice

Written **from inside**. The source is sincere. If they are wrong, they are wrong *honestly*, and the reader must work that out unaided.

**Do not soften. Do not wink. Do not editorialize.**

The strongest technique available: **let the source condemn itself in a sentence it thinks is a boast.**

> *"He stands in no caste. He wrote them."*

The Hierophancy wrote that with pride. It is the most damning line in the article.

### Register

- **No em-dashes.** No en-dashes. Recast the sentence; do not merely repunctuate. Use commas, colons, semicolons, or a full stop.
- **Sentences flow.** Parenthetical asides become their own sentences. Appositives become relative clauses.
- **Numbers:** spelled out when rhetorical ("three hundred and seventy-eight years"), digits when reference ("361 = 19²").
- **Grand, not purple.** The voice of a serious historical work with literary ambition. Gibbon, not a game manual.

### Structural devices

| Device | Effect |
|---|---|
| **Rebutting an unnamed accusation** | *"That the god was ever otherwise is a slander of the Reckoners, and is answered in the appendix."* An orthodoxy that footnotes its rebuttals has heard the charge. |
| **Diegetic redaction** | *"It is not held in this hand, and it is not written in this article."* The secret is preserved **in-world**, not by omission. Far more sinister than a gap. |
| **Word choice as tell** | *"The argument has been sufficient for eight hundred years."* **Sufficient**, not **true**. A scholar chose that word. |
| **Refusing a name** | The Enemy is called *Mania* throughout; her true name is noted as a form of λύσις and withheld. The document performs the erasure rather than describing it. |
| **Instruction to an in-world reader** | *"The provincial clergy are instructed to understand what follows, since it has cost several of them their lives."* Establishes audience, stakes, and institutional voice in one line. |

### In-world citation

Quotations are attributed to named in-world figures, with `[[TODO: ...]]` where the figure is not yet invented.

```markdown
> *"I have watched the sky for sixty years and never once seen it disobeyed.
> Then I come down from the tower, and I walk into the city."*
> **[[Anaxas]], Taxiarch Concordant**
```

### Links

Standard wiki double-brackets. Pipe for display text: `[[Emperor of Yavanna|Emperor]]`.

Link **every proper noun on first use**, even if the target does not exist yet. Red links are a to-do list.

---

## 4. The Apparatus

HTML comments. Two kinds.

### Inline comments

Placed immediately after the passage they concern. They carry:

- **the truth the source cannot see**
- **why the source is blind to it**
- **which counter-source holds the correction**

```markdown
<!--
    The Hierophancy cannot say that Monas was ever a brother, that Monē means
    "abiding" and came first, or that "alone" is a later re-hearing of the name.
    They believe the solitude is the god's nature and always was.

    The Reckoners hold the correction. See ledger.md.

    The ascetic discipline of Yavanna is a bereavement its practitioners have
    not been told about. Nobody in this document knows that.
-->
```

### The terminal apparatus

One block at the foot of the file. Carries:

- **counter-sources still to write**
- **TODOs** (calendar gaps, unnamed institutions, unratified proposals)
- **anything that is a fact about the *project* rather than about the world**

> **Rule:** *"The remaining sixteen months need names"* is not a fact about Yavanna. It is a fact about the project. **No in-world institution can hold it**, because no institution exists in a world where the months are undetermined. It goes in a comment. Always.

---

## The Source Register

Maintain in `index.md`. Every source, its bias, its blind spot.

| Source | Voice | Good for | Blind to |
|---|---|---|---|
| **The Hierophancy of Sophras** | Orthodox Eutaxian. Professing. Mathematically exact. | Doctrine, the calendar's mathematics, the official history | The cost of the Severance. Everything the faith took. |
| **The Reckoners / the Ledger** | Lysian. **A book of accounts, not a scripture.** | The debt. What was taken. The pre-Severance world. | Any good the empire has done in 800 years. |
| **Vestrn chronicle tradition** | Defeated, distant, self-governing, proud. | **That the war was won by luck** (they are the only ones who know). | Its own surrender. |
| **A philological body** *(unnamed)* | Scholarly, antiquarian. | The sound-laws. The strata beneath the names. | Overreads consonants. Sometimes catastrophically. |

### Rules for adding a source

**A source earns its existence only if it can be wrong.** It needs:

1. **A reason to know** — access, method, proximity
2. **A reason to write** — an interest, a grievance, an office
3. **A reason to distort** — something it *needs* to be true

If it has no motive to lie, delete it. It is not a source.

---

## Handling Open Questions

**Open questions do not appear in articles as questions.** They appear as **disputes**, which is strictly better.

| Bad (out-of-world question in an article) | Good (in-world dispute across articles) |
|---|---|
| *"Do the observatories serve the throne or check it? Both readings are supported."* | `eutaxia.md`: the Skopoi serve. `ledger.md`: a realm out of true has forfeited its mandate, **and here are the Skopoi's own texts proving it.** Neither can be dismissed. |
| *"The name of the old faith is unknown."* | `eutaxia.md`: *nowhere preserved.* `ledger.md`: **we have it, and we will not give it to you.** `eutaxia.md`: *they are lying.* **Both may be telling the truth.** |

A genuinely unanswered question goes in a **comment**, not in the body.

---

## Checklist Before Committing an Article

- [ ] Frontmatter complete. `reliability` names a specific blind spot.
- [ ] Authorial note lists what this source **cannot say**.
- [ ] Body contains **zero** out-of-world hedging. No "they believe that."
- [ ] Body contains **zero** em-dashes and en-dashes.
- [ ] At least one sentence the source thinks is a boast and the reader will read as a confession.
- [ ] Every fact in the body is something this source could plausibly know.
- [ ] Every fact the source **cannot** know is in a comment, routed to a named counter-source.
- [ ] All TODOs are in comments, never in the body.
- [ ] Proper nouns linked on first use.
- [ ] Terminal apparatus lists counter-sources still to write.
