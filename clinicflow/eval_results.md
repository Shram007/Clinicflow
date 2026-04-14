# ClinicFlow Evaluation Rubric

## Pipeline: SOAP Note Generation

| Test | Metric | Pass Criteria |
|------|--------|--------------|
| Structural correctness | All 6 SOAP keys present | 100% — zero missing keys |
| Content fidelity | Signal words from transcript appear in output | At least 1 signal per field |
| Generation latency | Time to complete | < 10 seconds per note |
| Self-correction | Fallback on bad LLM output | Valid VisitDetail with all keys |

## Running the eval
```bash
cd clinicflow
pytest backend/tests/eval_soap.py -v
```
