import os
from rich.progress import Progress
from rich.progress import SpinnerColumn
from rich.progress import TextColumn
from rich.progress import BarColumn
from rich.progress import TaskProgressColumn
from rich.progress import TimeElapsedColumn
from rich.progress import TimeRemainingColumn
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import defaultdict
import pandas as pd
import numpy as np
import contractions
from sqlalchemy import select
import spacy

from comp370.db import Client as Db
from comp370.db.models import Line
from comp370.db.models import Season
from comp370.db.models import Episode
from comp370.constants import DIR_DATA

nlp = spacy.load("en_core_web_sm")


def expand(text):
    words = []
    for word in text.split():
        words.append(contractions.fix(word))
    return " ".join(words)


def remove_names(text):
    doc = nlp(text)
    names = {ent.text.lower() for ent in doc.ents if ent.label_ == "PERSON"}
    return " ".join([w for w in text.split() if w.lower() not in names])


def preprocess_text(text):
    """Enhanced preprocessing with lemmatization and POS filtering"""
    # Expand contractions
    text = expand(text)

    # Use spaCy for lemmatization and POS filtering
    doc = nlp(text.lower())

    # Hardcoded list of Seinfeld main character names to remove
    character_names = {
        "jerry",
        "george",
        "elaine",
        "kramer",
        "newman",
        "costanza",
        "seinfeld",
        "benes",
        "morty",
        "helen",
        "izzy",
        "ray",
    }

    # Keep only nouns and adjectives (more distinctive than verbs)
    # Expanded list of generic verbs to exclude
    generic_verbs = {
        "be",
        "have",
        "do",
        "will",
        "would",
        "could",
        "should",
        "may",
        "might",
        "can",
        "must",
        "shall",
        "go",
        "get",
        "make",
        "know",
        "think",
        "tell",
        "come",
        "want",
        "look",
        "say",
        "ask",
        "need",
        "use",
        "let",
        "try",
        "seem",
        "happen",
        "mean",
        "give",
        "take",
        "find",
        "talk",
        "bring",
        "feel",
    }

    meaningful_tokens = []

    for token in doc:
        lemma = token.lemma_

        # Skip if it's a character name
        if lemma in character_names:
            continue

        # For NOUNS and ADJECTIVES - keep most of them
        if token.pos_ in ["NOUN", "ADJ", "PROPN"]:
            if (
                not token.is_stop
                and not token.is_punct
                and len(token.text) > 2
                and token.text.isalpha()
            ):
                meaningful_tokens.append(lemma)

        # For VERBS - only keep specific action verbs
        elif token.pos_ == "VERB":
            if (
                lemma not in generic_verbs
                and not token.is_stop
                and not token.is_punct
                and len(token.text) > 2
                and token.text.isalpha()
            ):
                meaningful_tokens.append(lemma)

    return " ".join(meaningful_tokens)


def is_meaningful_ngram(term, min_ngram_size=2):
    """
    Check if an n-gram is a meaningful phrase (named entity, fixed expression)
    rather than just a random combination of words.

    Args:
        term: the n-gram string
        min_ngram_size: minimum size to check (1-grams always pass)
    """
    words = term.split()

    # Unigrams are always meaningful
    if len(words) < min_ngram_size:
        return True

    # Parse the n-gram with spaCy
    doc = nlp(term)

    # Check if it's a named entity (places, organizations, products, etc.)
    if doc.ents:
        return True

    # Check if it contains mostly proper nouns (likely a name/place)
    propn_count = sum(1 for token in doc if token.pos_ == "PROPN")
    if propn_count >= len(words) - 1:  # allow one non-proper noun
        return True

    # Check if it's a compound noun phrase (all nouns/adjectives)
    # These are often meaningful fixed expressions
    pos_tags = [token.pos_ for token in doc]
    if all(pos in ["NOUN", "ADJ", "PROPN"] for pos in pos_tags):
        return True

    # Reject if it contains a verb (likely an action phrase like "steal wallet")
    if any(token.pos_ == "VERB" for token in doc):
        return False

    # Default: accept other cases
    return True


def tf_idf_by_category(row, top_k=15, min_df=3, max_df=0.7, max_ngram=4):
    """
    Improved TF-IDF with stricter filtering and redundant n-gram removal

    Args:
        row: list of (dialogue, category) tuples
        top_k: number of top words to return per category
        min_df: minimum document frequency (increased to filter rare terms)
        max_df: maximum document frequency (decreased to filter common terms)
        max_ngram: maximum n-gram size (e.g., 2 for bigrams, 3 for trigrams)
    """
    dialogues = [d for d, c in row]
    categories = [c for d, c in row]

    # Enhanced TF-IDF with stricter parameters
    vec = TfidfVectorizer(
        lowercase=True,
        stop_words="english",
        min_df=min_df,  # must appear in at least 3 documents
        max_df=max_df,  # can't appear in more than 70% of documents
        ngram_range=(1, max_ngram),  # unigrams up to max_ngram
        max_features=3000,  # limit vocabulary size
    )

    X = vec.fit_transform(dialogues)
    vocab = np.array(vec.get_feature_names_out())

    # Group rows by category
    cat_indices = defaultdict(list)
    for i, c in enumerate(categories):
        cat_indices[c].append(i)

    results = {}

    # Calculate global average
    global_avg = X.mean(axis=0).A1

    for cat, idxs in cat_indices.items():
        # Get category-specific TF-IDF
        cat_vec = X[idxs].mean(axis=0).A1

        # Calculate distinctiveness ratio instead of difference
        # This handles categories of different sizes better
        distinctiveness = np.divide(
            cat_vec,
            global_avg + 1e-10,  # avoid division by zero
            out=np.zeros_like(cat_vec),
            where=global_avg > 1e-10,
        )

        # Combined score: TF-IDF weighted by distinctiveness
        # Only keep terms that are at least 1.5x more common in this category
        score = cat_vec * distinctiveness

        # Get ALL terms sorted by score
        all_idx_sorted = np.argsort(score)[::-1]

        # Filter: keep only terms with distinctiveness ratio > 1.5
        filtered_idx = [idx for idx in all_idx_sorted if distinctiveness[idx] > 1.5]

        # Remove redundant n-grams
        # Group terms by n-gram size (descending order - longest first)
        ngram_groups = defaultdict(list)
        for idx in filtered_idx:
            term = vocab[idx]
            n = len(term.split())  # n-gram size

            # Only keep meaningful n-grams
            if is_meaningful_ngram(term):
                ngram_groups[n].append((idx, term, cat_vec[idx], distinctiveness[idx]))

        # Collect words that appear in longer n-grams
        # Start with longest n-grams and work down
        used_words = set()
        non_redundant_terms = []

        for n in sorted(ngram_groups.keys(), reverse=True):
            for idx, term, tfidf, dist in ngram_groups[n]:
                words = set(term.split())

                # Check if this n-gram has ANY overlap with already used words
                # If ANY word is already used, skip this n-gram as redundant
                if words & used_words:  # intersection - any overlap
                    continue  # skip this redundant n-gram

                # This n-gram is not redundant, keep it
                non_redundant_terms.append((idx, term, tfidf, dist))
                used_words.update(words)

        # Sort by score and take top k
        non_redundant_terms.sort(key=lambda x: score[x[0]], reverse=True)
        top_terms = non_redundant_terms[:top_k]

        results[cat] = [
            (term, float(tfidf), float(dist)) for _, term, tfidf, dist in top_terms
        ]

    return results


def main():
    df_in = pd.read_csv(DIR_DATA / "annotations" / "annotations.derived.csv")
    rows = []
    total = len(df_in)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        TimeRemainingColumn(),
    ) as bar:
        step = bar.add_task("Getting and preprocessing dialogue...", total=total)
        with Db().session() as db:
            for _, row in df_in.iterrows():
                line = (
                    db.execute(
                        (
                            select(Line)
                            .join(Line.episode)
                            .join(Episode.season)
                            .where(
                                Season.number == row["season_number"],
                                Episode.number == row["episode_number"],
                                Line.number == row["line_number"],
                            )
                        )
                    )
                    .scalars()
                    .first()
                )

                dialogue = line.dialogue
                dialogue = preprocess_text(dialogue)

                # Only include if there's meaningful content after preprocessing
                if dialogue.strip():
                    rows.append((dialogue, row["category"]))

                bar.update(step, advance=1)

    rows = set(rows)
    rows = list(rows)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
    ) as bar:
        step = bar.add_task("Computing TF-IDF...", total=1)
        results = tf_idf_by_category(rows, top_k=15)
        bar.update(step, advance=1)

    df_out = pd.DataFrame(
        columns=[
            "category",
            "word",
            "score",
            "distinctiveness",
        ]
    )

    # Sort categories alphabetically
    for cat in sorted(results.keys()):
        if cat in ["Miscellaneous", "UNKNOWN"]:
            continue
        terms = results[cat]
        for term, score, distinctiveness in sorted(terms, key=lambda x: -x[1]):
            df_out.loc[len(df_out)] = [cat, term, score, distinctiveness]

    # Output
    os.makedirs(DIR_DATA / "statistics", exist_ok=True)
    df_out.to_csv(DIR_DATA / "statistics" / "statistics.tfidf.csv", index=False)


if __name__ == "__main__":
    main()
