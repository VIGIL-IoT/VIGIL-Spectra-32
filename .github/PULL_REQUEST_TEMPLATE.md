## Summary

<!-- What changed and why? -->

## Evidence and checks

- [ ] `python -m unittest discover -s tests -v`
- [ ] `python -m compileall -q data services components simulator tests`
- [ ] `python tools/check_docs.py`
- [ ] Documentation and traceability updated

## Validation boundary

- [ ] Software model only
- [ ] Local broker integration (include versions/configuration)
- [ ] Physical hardware (include board, firmware hash, and safe lab setup)
- [ ] Not run (explain why)

## Safety and data

- [ ] No unauthorized target, secret, raw capture, or identifying serial log is included
- [ ] Any third-party code/data/font/model license and notice is preserved
- [ ] Simulated outcomes are not presented as hardware measurements
