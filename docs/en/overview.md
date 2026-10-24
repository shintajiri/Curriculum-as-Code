# Curriculum as Code — overview (English)

**Keep the source of truth of a degree programme's curriculum in structured data, generate the derived documents from it, and let a machine catch the formal errors.**

## Why

- A new faculty has to build a curriculum of 200+ courses from scratch.
- For quality assurance you want to design, from the start, *which course develops which programme learning outcome (PLO / "DP" in Japan)*.
- When syllabi, the PLO policy, the curriculum map and the assessment specification are maintained separately, every change to shared information (a PLO's name, a course–PLO mapping) has to be made in several places, and something is missed.

## How

```yaml
dp_definitions:            # PLOs: ID and name, defined once
  DP1: <outcome name>
courses:
  - id: <course id>
    name: <course name>
    goals: {G1: <learning goal>, G2: <learning goal>}
    dp: {DP1: introductory}            # PLOs referenced by ID, with a level
    assessments:
      - {method: report, weight: 60, goals: [G1]}   # weight in %, goals by ID
```

- Source of truth: the PLO definitions and the course definitions (version-controlled).
- Generated: the PLO section of each syllabus, the curriculum map (HTML/CSV).
- Checked by machine: dangling PLO IDs, dangling goal IDs, weights that do not sum to 100, duplicate course IDs.
- Judged by humans: whether goals and assessments correspond educationally, whether the levels are placed sensibly.

## What it is not

- No grades or personal data in these files; attainment is computed from separately managed learning-outcome data.
- Rubrics and aggregation rules are out of scope here.
- Putting the curriculum in YAML does not make it coherent by itself; it makes the gaps visible.

## Tools

```sh
pip install -r requirements.txt
python3 tools/validate.py examples/curriculum.example.yaml
python3 tools/generate.py examples/curriculum.example.yaml out/
```

See `docs/workflow.md` for the source → generate → check → human approval loop, which mirrors the operating practice in the companion repository **AcademicOps**.

License: documents CC BY 4.0, code MIT. Concept: Shintaro Tajiri.
