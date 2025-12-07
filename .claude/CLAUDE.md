# Advent of Management - Project Guide

## Overview

Advent of Management is a parody of Advent of Code where programming puzzles become corporate dysfunction scenarios at North Pole Operations, Inc. Players navigate middle-management challenges instead of writing code.

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Advent of Code │────▶│ Scenario Gen    │────▶│ S3 Bucket       │
│  (puzzles)      │     │ (Claude API)    │     │ (public hosting)│
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                         │
                                                         ▼
                                                ┌─────────────────┐
                                                │ Players         │
                                                │ (Claude/ChatGPT)│
                                                └─────────────────┘
```

## Key Files

| File | Purpose |
|------|---------|
| `prompts/clause_prompt.md` | Main game prompt (give to Claude/ChatGPT) |
| `prompts/scenario_prompt.md` | Prompt for generating new scenarios |
| `s3_content/game_rules.md` | Game mechanics, scoring, save codes |
| `s3_content/tone_guide.md` | NPC personalities, welcome message |
| `s3_content/cast.md` | Character roster |
| `src/scenario_gen.py` | Scenario generation from AoC puzzles |
| `src/publisher.py` | S3 upload utilities |
| `src/aoc_client.py` | Advent of Code puzzle fetcher |

## Environment Variables (.env)

```
AOC_SESSION_COOKIE=<from browser cookies on adventofcode.com>
ANTHROPIC_API_KEY=<for scenario generation>
AWS_ACCESS_KEY_ID=<for S3 publishing>
AWS_SECRET_ACCESS_KEY=<for S3 publishing>
AWS_REGION=us-east-1
S3_BUCKET_NAME=advent-of-management
AOC_YEAR=2025
```

## S3 Bucket Structure

```
advent-of-management.s3.us-east-1.amazonaws.com/
└── 2025/
    ├── manifest.json      # Available days, total_days
    ├── game_rules.md      # Scoring, career track, save codes
    ├── tone_guide.md      # NPC personalities, tone
    ├── cast.md            # Character roster
    ├── openapi.yaml       # For ChatGPT Actions
    ├── day1.json          # Scenario with 6 difficulty levels
    ├── day2.json
    └── ...
```

## Common Operations

### Generate and Publish a New Day

```python
cd "/Users/hammer/Software Development/Open Source/advent-of-management"
source venv/bin/activate
python -m src.main --day 8  # Generate day 8
```

Or manually:

```python
from src.aoc_client import AoCClient
from src.scenario_gen import ScenarioGenerator
from src.publisher import S3Publisher

aoc = AoCClient(os.environ['AOC_SESSION_COOKIE'], year=2025)
generator = ScenarioGenerator(os.environ['ANTHROPIC_API_KEY'])
publisher = S3Publisher(
    bucket_name='advent-of-management',
    aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
    region='us-east-1'
)

puzzle = aoc.get_puzzle(8)
scenario = generator.generate(puzzle)
url = publisher.publish_scenario(scenario)
publisher.update_manifest(2025, 8, total_days=12)
```

### Update Game Rules or Tone (Hot Update)

Edit the file in `s3_content/`, then upload:

```python
import boto3
s3 = boto3.client('s3', ...)
s3.put_object(
    Bucket='advent-of-management',
    Key='2025/game_rules.md',
    Body=open('s3_content/game_rules.md').read(),
    ContentType='text/markdown',
    CacheControl='max-age=300'
)
```

### Check Current Manifest

```bash
curl -s https://advent-of-management.s3.us-east-1.amazonaws.com/2025/manifest.json | jq
```

## Game Mechanics

### Career Track (6 Levels)

| Level | Title | Points Needed |
|-------|-------|---------------|
| 1 | Team Lead | 0 (start) |
| 2 | Supervisor | 5 |
| 3 | Manager | 12 |
| 4 | Director | 22 |
| 5 | VP | 35 |
| 6 | C-Suite | 50 |

### Scoring

- 3 stars (at/under par) = 3 points
- 2 stars (1-2 over par) = 2 points
- 1 star (3-4 over par) = 1 point
- 0 stars (5+ over par) = 0 points

### Save Code Format

```
AOM25-L{level}-D{day}-T{turns}-P{points}-R{ratings}
```

Example: `AOM25-L3-D7-T28-P16-R3322210`

### Secret Commands

- `!career` / `!level` - Show career status
- `!setlevel N` - Set difficulty level
- `!levels` - Show career ladder
- `!stats` - Detailed statistics
- `!day N` / `!goto N` - Jump to specific day
- `!refresh` - Re-fetch manifest for new days

## Platform Support

### Claude (Primary)

Works out of the box. Just paste the prompt from `prompts/clause_prompt.md`.

### ChatGPT

Requires additional setup. The prompt includes detection and offers users two options:

1. **Knowledge Files**: Download game files and upload to Custom GPT
2. **GPT Actions**: Import `openapi.yaml` schema

## AWS Cost Management

### Expected Costs

| Scenario | Monthly Cost |
|----------|--------------|
| Normal use (1K players) | < $0.01 |
| Viral (100K players) | ~$2 |
| Under attack | $0 - $400+ |

### Billing Alert Setup

1. AWS Console → Billing → Budgets → Create budget
2. Choose "Cost budget"
3. Set budget: $10/month
4. Add alert at 80% threshold
5. Enter email for notifications

### If Costs Spike (Add CloudFront)

1. CloudFront → Create distribution
2. Origin: `advent-of-management.s3.us-east-1.amazonaws.com`
3. Viewer protocol: Redirect HTTP to HTTPS
4. Cache policy: CachingOptimized
5. Update URLs in `clause_prompt.md` to use CloudFront domain

CloudFront provides:
- Edge caching (fewer S3 requests)
- DDoS protection (AWS Shield Standard, free)
- Can add WAF for rate limiting if needed

### If Under Attack (Add WAF)

1. WAF → Create web ACL
2. Add rate-based rule: 1000 requests/5 min per IP
3. Associate with CloudFront distribution

Cost: ~$5/month base + $1 per million requests

## 2025 Season Configuration

- **Total days**: 12 (not 25 like typical AoC)
- **Day 12**: Finale challenge before Christmas
- **Manifest**: `total_days: 12`

## Troubleshooting

### Scenario generation fails

Check:
- `AOC_SESSION_COOKIE` is valid (expires annually)
- `ANTHROPIC_API_KEY` has credits
- AoC puzzle is available (releases at midnight EST)

### Players can't fetch from S3

Check:
- Bucket policy allows public read
- Files have correct Content-Type
- No typos in URLs

### ChatGPT not showing setup instructions

The prompt relies on self-identification. If ChatGPT ignores it:
- User can manually type "I'm using ChatGPT"
- Or just say "offline" to use fallback mode
