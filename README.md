<div align="center">

# ✦ The Black Shard ✦

> *"A world remembered in pieces — and never twice the same."*

![Status](https://img.shields.io/badge/status-under_construction-orange?style=for-the-badge)
![Stage](https://img.shields.io/badge/stage-pre--alpha-blue?style=for-the-badge)
![World](https://img.shields.io/badge/world-Weilan-blueviolet?style=for-the-badge)
![Faith](https://img.shields.io/badge/faith-Eutaxia-red?style=for-the-badge)
![Sources](https://img.shields.io/badge/sources-unreliable_by_design-lightgrey?style=for-the-badge)
![License](https://img.shields.io/badge/license-CC_BY--NC-lightgrey?style=for-the-badge)

---

*Worldbuilding archive of lore, history, cultures, languages, calendars, and testimony.*

</div>

---

## 🌍 The Paracosm

**The Black Shard** is a high fantasy universe with a focus on linguistics and high concept political intrigue. I use it as a setting for roleplaying games but it exists outside of that. I would continue worldbuilding even if I could never play D&D again.

This repository is a canonical archive, but it is not a wiki of settled facts, rather it is a **collection of testimonies**: each entry about the world is written from an in-universe perspective. Thus primary sources contradict one another, and each chronicler has a voice/bias: composed from inside a faith, court, or grievance, each with its own silences.

No single document here is *the truth.* The truth is what survives being read against everything else.

Nobody in-universe knows the world by the name "the Black Shard". To them, the world is the continent, **Weilan**. 

---

## ✨ Core Philosophy

> This is not a story.
>
> It is a **world**, and stories only pass through it.
>
> Every nation has a history.
> Every faith has a heresy.
> Every map has a lie on it somewhere.
>
> Every source here has an author.
> Every author has a reason to shade the truth.
> The record does not agree with itself — and that is not a flaw. **That is the point.**
>
> The goal is not perfection.
> The goal is *believability* — the weight of a world too large for any one voice to hold.

---

## 📂 Repository Structure

> *Proposed layout — the archive is young; most branches are still empty. Files marked* `← drafted` *exist today.*

```text
.
├── docs/
│   ├── cosmology/
│   ├── history/
│   ├── nations/
│   │   ├── yavanna/
│   │   └── vestrn/
│   ├── religions/
│   │   └── eutaxia.md                  ← drafted
│   ├── peoples/
│   ├── cultures/
│   ├── languages/
│   │   └── languages_of_weilan.csv     ← drafted
│   └── technology/
│
├── reference/
│   └── calendar.json                   ← drafted
│
├── characters/
├── timelines/
├── stories/
├── maps/
│
├── assets/
│   ├── artwork/
│   ├── flags/
│   └── symbols/
│
└── README.md
```

---

## 🗂 The Archive So Far

| File | What it holds |
|---|---|
| 📜 `eutaxia.md` | The doctrine of **Eutaxia** — *good order* — written from inside the orthodox imperial church: its gods, its calendar theology, its deathless Emperor, and the heresies it fears. |
| 🗓 `calendar.json` | The machine-readable **Calendar of Yavanna** — a 361-day year, a seven-day week, and two moons (Iso and Sisar) kept in their courses. |
| 🗣 `languages_of_weilan.csv` | Eleven **languages of Weilan**, each with its homeland and the real-world tongue it is shaped after. |

<details>
<summary><b>🕊 The Seven Who Hold the Days</b></summary>

<br>

In Eutaxia, to hold a day of the week *is* to be a god. There are seven — the **Hebdomad** — and above them, holding no day and yet second to none in heaven or earth, the deathless Emperor.

| God | Day | Domains |
|---|---|---|
| **Monas** | Monda | The Great Moon, solitude, asceticism, reflection, the cosmos |
| **Theureus** | Tuesda | Authority, sovereignty, caste, just war |
| **Firēs** | Wirsda | Wind, breath, sky, fate, travelers, messages |
| **Barjas** | Horda | Judgment, storms, the thunderbolt, trials, mountains |
| **Phira** | Frida | Love, marriage, fertility, union, sacred oaths |
| **Sophras** | Sorda | Wisdom, philosophy, the arcane arts, agriculture, time, prophecy |
| **Sounia** | Sunda | The sun, fire, illumination, cosmic order, fulfillment |

*Once the Seven were Eight. The eighth is not named here.*

</details>

<details>
<summary><b>🗣 The Tongues of Weilan</b></summary>

<br>

Eleven languages are recorded so far, each rooted in its own homeland across the region.

| Language | Homeland |
|---|---|
| High Vestrn | Hojland |
| Low Vestrn | Sarvaald / Ríkrvollr |
| Duegar | Nuruu |
| Bahari | Albahaar |
| Havari | Havaari |
| Hskan | Hanzith |
| Ojapól | Hoja plata |
| Myridic | Myridian |
| D'gento | Valle d'argento |
| Yona | Southern Yavanna |
| Doran | Northern Yavanna |

*Each language's real-world analog is recorded in the source file.*

</details>

---

## 🧭 Canon & Testimony

The archive tracks **two separate things**, and keeps them apart on purpose.

**Canon status** — is this settled?

| Level | Meaning |
|---|---|
| ✅ Canon | Official lore |
| 🟨 Draft | Being developed |
| 🟪 Experimental | May change drastically |
| ❌ Deprecated | No longer canon |

**Source reliability** — *can this narrator be trusted?* Every in-world document carries frontmatter declaring where it comes from and how far it can be believed:

| Field | Meaning |
|---|---|
| `source` | The in-world author or tradition |
| `perspective` | Its viewpoint and allegiances |
| `reliability` | What it gets right — and where it is silent, biased, or wrong |
| `status` | Draft · in progress · settled |

A document can be **✅ canon** and still be a **liar**. That tension is the whole design.

---

## 🌌 Current Scope

- [x] Calendar & timekeeping
- [x] A major faith (Eutaxia)
- [x] Foundational languages
- [ ] Cosmology
- [ ] Geography & climate
- [ ] Historical eras & timeline
- [ ] Complete political map
- [ ] Nation articles
- [ ] Peoples & cultures
- [ ] Character database
- [ ] Historical atlas
- [ ] Encyclopaedia

---

## 📖 World Statistics

```text
Imperial Year        :: 812
Region               :: Weilan
Documented Realms    :: Yavanna Empire · Duchies of Vestrn
Languages Recorded   :: 11
Major Faiths         :: Eutaxia  (+ the Reckoner heresy)
Moons                :: 2   (Iso · Sisar)
Continents           :: ???
Cities               :: ???
Characters           :: ???
Stories              :: ???
```

---

## 🎨 Influences & Design DNA

*Evident in the material — swap in your own as the project grows:*

- Comparative **linguistics** and language families
- Real-world **religious history**, schism, and calendar reform
- **Greek and Sanskrit** sacred vocabulary as a founding stratum
- The epistemics of **unreliable historical sources** — chronicles, scripture, and heresy that refuse to agree

---

## 🗺 Development Roadmap

- [ ] Draft the cosmology and the shape of the heavens
- [ ] Chart the geography of Weilan
- [ ] Build the historical timeline (Unification, the Severance, the present day)
- [ ] Write the nation articles — Yavanna, then the Duchies of Vestrn
- [ ] Give voice to the counter-testimony (the Reckoners; the frontier chronicles)
- [ ] Expand the language documentation into scripts and grammar
- [ ] Compile the encyclopaedia
- [ ] An interactive atlas & searchable wiki

---

<details>
<summary><b>🌠 Lore Teaser</b></summary>

<br>

Once, the week had eight days.

One of them was struck from the calendar — and the goddess who held it was struck from the sky.

She has been running ever since. Seven nights out, seven nights home, over the heads of a people who cast her down and then, out of pity, kept giving her a day. An Emperor took even that away.

The empire calls this *order.*

She has never once stopped keeping time.

</details>

---

<div align="center">

### *"Every civilization believes it is standing at the end of history.*
### *None of them were right."*

</div>
