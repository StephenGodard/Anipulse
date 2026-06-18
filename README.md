# AniPulse

Agent autonome de content factory pour AnimeSphere.

AniPulse remplit chaque jour le planning editorial avec des contenus a valider:

- idees SEO et articles anime de saison;
- scripts TikTok/Reels;
- posts X/Twitter reactifs;
- contenus Reddit ou Instagram en bonus.

AniPulse ne publie pas automatiquement. Il prepare, programme et met les contenus en `A valider`; Stephen relit, valide et publie.

## MVP

Le MVP est volontairement Python-first:

1. Lire `data/x_samples.json`, compose de posts X copies/colles.
2. Verifier que les anime detectes existent sur AnimeSphere via `https://animesphere.io/api/anime/search?title=`.
3. Scorer les opportunites selon la pertinence AnimeSphere et les signaux fan/react.
4. Generer 4 contenus par run: 1 SEO, 1 TikTok, 2 X/Twitter.
5. Creer une page Notion par contenu dans le planning global avec le statut `A valider`.
6. Envoyer un recap email via Resend quand la configuration est presente.
7. Laisser la validation humaine avant publication.

## Installation

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e .
cp .env.example .env
```

## Configuration

Les secrets restent dans `.env`:

- `OPENAI_API_KEY`: active la generation LLM. Sans cle, AniPulse utilise un brouillon de fallback pour la demo.
- `ANIPULSE_SOURCE`: `sample` pour `data/x_samples.json`, `x-api` pour l'API X.
- `X_API_TOKEN`, `X_ACCOUNTS`, `X_MAX_RESULTS`: activent la collecte X reelle.
- `ANIPULSE_TRACKED_TITLES`: titres anime a detecter dans les tweets.
- `NOTION_TOKEN` et `NOTION_CONTENT_CALENDAR_DB_ID`: activent l'ecriture dans le planning Notion.
- `NOTION_FALLBACK_PAGE_ID`: page Notion parent utilisee si la database calendrier est indisponible.
- `RESEND_API_KEY`, `RESEND_FROM_EMAIL`, `RESEND_TO_EMAIL`: activent le recap email.

## Utilisation

Dry-run lisible:

```bash
anipulse --dry-run
```

Dry-run JSON:

```bash
anipulse --dry-run --json
```

Ecriture Notion + email, si les variables sont configurees:

```bash
anipulse --write
```

Collecte depuis l'API X:

```bash
ANIPULSE_SOURCE=x-api anipulse --dry-run --json
```

Export de secours JSON + Markdown:

```bash
anipulse --dry-run --export-dir exports
```

Test email Resend sans recreer d'events Notion:

```bash
anipulse --send-email --skip-notion --limit 4 --export-dir exports
```

## Execution quotidienne

Un workflow GitHub Actions est disponible dans `.github/workflows/anipulse-daily.yml`.
Par defaut il tourne en dry-run via `ANIPULSE_DRY_RUN=true`.

Pour activer l'ecriture Notion et le recap Resend, configurer:

- secrets: `OPENAI_API_KEY`, `NOTION_TOKEN`, `NOTION_CONTENT_CALENDAR_DB_ID`, `RESEND_API_KEY`;
- variables: `ANIPULSE_DRY_RUN=false`, `NOTION_FALLBACK_PAGE_ID`, `RESEND_FROM_EMAIL`, `RESEND_TO_EMAIL`.

Pour la demo hackathon, `NOTION_CONTENT_CALENDAR_DB_ID` pointe vers la database dediee `Planning AniPulse`, creee sous `Plan de communication globale`.

## Nice-to-have

Hermes, OpenClaw ou d'autres outils video peuvent etre testes plus tard, uniquement si la boucle principale est stable.
