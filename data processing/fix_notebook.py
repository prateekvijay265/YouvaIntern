"""
Comprehensive patch for data_preprocessing_pipeline.ipynb.
Fixes all references to columns that don't exist in seaborn's Titanic:
  - No 'name', 'ticket', 'cabin' columns
  - Available columns: survived, pclass, sex, age, sibsp, parch, fare,
    embarked, class, who, adult_male, deck, embark_town, alive, alone

Fixes applied:
  F1: Step 3.2 - remove 'who' from drop list (use for FE)
  F2: Step 5.2 - replace name->title extraction with who->title mapping
  F3: Step 5.7 - replace raw_df['cabin'] with df['deck'].notnull()
  F4: Step 5.9 - drop 'who' instead of 'name'/'ticket'
  F5: Phase 3 & 5 markdown tables updated
  F6: Final summary updated
"""
import json

NOTEBOOK = "data_preprocessing_pipeline.ipynb"

with open(NOTEBOOK, encoding="utf-8") as f:
    nb = json.load(f)


def cell_src(cell):
    src = cell.get("source", [])
    if isinstance(src, list):
        return "".join(src)
    return src


def set_src(cell, new_src):
    cell["source"] = new_src.splitlines(keepends=True)


fixes_applied = []

for idx, cell in enumerate(nb["cells"]):
    src = cell_src(cell)

    # ── F1: Step 3.2 cols_to_drop ──────────────────────────────────────────
    if "cols_to_drop = ['deck', 'alive', 'who', 'adult_male', 'class', 'embark_town']" in src:
        new_src = src.replace(
            "cols_to_drop = ['deck', 'alive', 'who', 'adult_male', 'class', 'embark_town']",
            (
                "# Note: 'who' is kept for FE (Step 5.2). 'deck' is kept to derive has_cabin.\n"
                "# seaborn Titanic has NO 'name', 'ticket', or 'cabin' columns.\n"
                "cols_to_drop = ['alive', 'adult_male', 'class', 'embark_town']"
            ),
        )
        set_src(cell, new_src)
        fixes_applied.append("F1: cols_to_drop updated")

    # Also handle already-patched version (from previous run)
    elif ("cols_to_drop = ['deck', 'alive', 'adult_male', 'class', 'embark_town']" in src
          and "Note: 'who' is kept" in src):
        new_src = src.replace(
            "cols_to_drop = ['deck', 'alive', 'adult_male', 'class', 'embark_town']",
            "cols_to_drop = ['alive', 'adult_male', 'class', 'embark_town']",
        )
        set_src(cell, new_src)
        fixes_applied.append("F1b: cols_to_drop re-patched (removed deck)")

    # ── F2: Step 5.2 title extraction ──────────────────────────────────────
    if ("df['title'] = df['name'].apply(extract_title)" in src or
            "df['title'] = df['who'].map(person_type_mapping)" in src):
        new_cell_src = (
            "# ── Step 5.2: Person Type from 'who' column ─────────────────────────────────\n"
            "# seaborn's Titanic provides a 'who' column: 'man', 'woman', 'child'.\n"
            "# This encodes the same signal as a social title (gender + age proxy).\n"
            "# We map it to a 'title' feature for consistency with domain terminology.\n"
            "#\n"
            "#   'man'   -> 'Mr'        (adult male)\n"
            "#   'woman' -> 'Mrs_Miss'  (adult female)\n"
            "#   'child' -> 'Child'     (highest rescue priority)\n"
            "\n"
            "person_type_mapping = {\n"
            "    'man':   'Mr',\n"
            "    'woman': 'Mrs_Miss',\n"
            "    'child': 'Child',\n"
            "}\n"
            "df['title'] = df['who'].map(person_type_mapping).fillna('Mr')\n"
            "\n"
            "print('Title (person_type) created from who column.')\n"
            "print(df['title'].value_counts().to_string())\n"
        )
        set_src(cell, new_cell_src)
        fixes_applied.append("F2: title extraction replaced with who-mapping")

    # ── F3: Step 5.7 has_cabin ─────────────────────────────────────────────
    if "raw_df['cabin'].notnull()" in src or "df['cabin']" in src:
        new_src = src.replace(
            "df['has_cabin'] = raw_df['cabin'].notnull().astype(int)",
            (
                "# seaborn's Titanic has 'deck' (not 'cabin') — a derived column\n"
                "# where NaN means the passenger's deck assignment was unknown.\n"
                "# Passengers with a known deck were typically 1st-class/wealthier.\n"
                "df['has_cabin'] = df['deck'].notnull().astype(int)"
            ),
        )
        # Also fix the comment block referencing 'cabin'
        new_src = new_src.replace(
            "# 'cabin' column exists in the raw data but was almost fully null.\n"
            "# However, whether a cabin number is RECORDED is itself informative:\n"
            "# 1st class passengers almost always had cabin info; 3rd class rarely did.",
            (
                "# 'deck' in seaborn's Titanic is NaN for most 3rd-class passengers.\n"
                "# Whether a deck is RECORDED signals wealth/class status."
            ),
        )
        set_src(cell, new_src)
        fixes_applied.append("F3: has_cabin now uses df['deck']")

    # ── F4: Step 5.9 drop columns ──────────────────────────────────────────
    if "df.drop(columns=['name', 'ticket'], inplace=True)" in src:
        new_src = src.replace(
            "# 'name' and 'ticket' are high-cardinality free-text — too noisy without deep NLP.\n"
            "# 'cabin' was used for 'has_cabin'; now discard the raw column.\n"
            "# 'sibsp' and 'parch' are now encoded in 'family_size'.\n"
            "df.drop(columns=['name', 'ticket'], inplace=True)",
            (
                "# Drop columns that have served their purpose:\n"
                "#   'who'  -> used to create 'title'; redundant now\n"
                "#   'deck' -> used to create 'has_cabin'; high missingness, raw form not useful\n"
                "# 'sibsp' and 'parch' are now encoded in 'family_size'.\n"
                "df.drop(columns=['who', 'deck'], inplace=True)"
            ),
        )
        set_src(cell, new_src)
        fixes_applied.append("F4: Step 5.9 drops who+deck instead of name/ticket")

    # Also fix already-patched version
    elif "df.drop(columns=['who'], inplace=True)" in src and "deck" not in src:
        new_src = src.replace(
            "df.drop(columns=['who'], inplace=True)",
            "df.drop(columns=['who', 'deck'], inplace=True)",
        )
        set_src(cell, new_src)
        fixes_applied.append("F4b: Added deck to drop list")

    # ── F5: Phase 3 markdown — 'deck' strategy updated ─────────────────────
    if cell["cell_type"] == "markdown" and "| `deck` |" in src and "Drop column" in src:
        new_src = src.replace(
            "| `deck` | ~77% | Drop column | Too sparse to be useful |",
            "| `deck` | ~77% | **Kept for FE** | Used to derive `has_cabin`; dropped after |",
        )
        set_src(cell, new_src)
        fixes_applied.append("F5a: Phase 3 markdown deck row updated")

    if cell["cell_type"] == "markdown" and "| `who` | 0% |" in src:
        if "Drop (redundant)" in src:
            new_src = src.replace(
                "| `who` | 0% | Drop (redundant) | Derives from `sex` + `age` |",
                "| `who` | 0% | **Kept for FE** | Mapped to `title` (man/woman/child) |",
            )
            set_src(cell, new_src)
            fixes_applied.append("F5b: Phase 3 markdown who row updated")

    # ── F5c: Phase 5 FE table — title row ──────────────────────────────────
    if cell["cell_type"] == "markdown" and "| `title` |" in src and "name" in src:
        new_src = src.replace(
            "| `title` | `name` | Social title (Mr, Mrs, Miss, Master) encodes age + sex + class |",
            "| `title` | `who` | Person type (Mr / Mrs_Miss / Child) — encodes age + sex signal |",
        )
        set_src(cell, new_src)
        fixes_applied.append("F5c: Phase 5 FE table title row updated")

    # ── F6: Final summary cell ─────────────────────────────────────────────
    if "title         — social title from name" in src:
        new_src = src.replace(
            "   ✅ title         — social title from name",
            "   ✅ title         — person type from who (Mr / Mrs_Miss / Child)",
        )
        set_src(cell, new_src)
        fixes_applied.append("F6: Final summary title line updated")

    if "has_cabin     — cabin record presence" in src:
        new_src = src.replace(
            "   ✅ has_cabin     — cabin record presence",
            "   ✅ has_cabin     — deck record presence (proxy for wealth/class)",
        )
        set_src(cell, new_src)
        fixes_applied.append("F6b: Final summary has_cabin line updated")

# ── Pipeline demo cell also drops 'cabin' ─────────────────────────────────
for cell in nb["cells"]:
    src = cell_src(cell)
    if "'cabin'" in src and "raw_clean" in src and cell["cell_type"] == "code":
        new_src = src.replace(
            "raw_clean.drop(columns=['deck', 'alive', 'who', 'adult_male', 'class',\n"
            "                         'embark_town', 'name', 'ticket', 'cabin'], inplace=True)",
            "raw_clean.drop(columns=['alive', 'adult_male', 'class', 'embark_town'], inplace=True)",
        )
        if new_src != src:
            set_src(cell, new_src)
            fixes_applied.append("F7: Pipeline demo drop list fixed")

# Save
with open(NOTEBOOK, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print("Notebook saved.")
print(f"Fixes applied ({len(fixes_applied)}):")
for fix in fixes_applied:
    print(f"  - {fix}")
