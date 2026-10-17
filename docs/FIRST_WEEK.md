# First week — practical group checklist

### Nadula (shared system + binomial)
- [x] Initial FastAPI repository and topic contract
- [x] First working Binomial Expressions generator and SymPy validation
- [x] REST API for questions, submissions and teacher summary
- [ ] Sketch shared student UI and teacher dashboard
- [ ] Add authentication before testing with real students
- [ ] Add the approved LLM provider and *verify every generated result*

### Bopage — Factorization
- [ ] Study the topic contract and implement `factorization.py`
- [ ] Define at least three teacher-reviewed misconceptions
- [ ] Generate 20 varied questions and automated checks

### Nimsara — Equations
- [ ] Implement `equations.py` using SymPy solving and checking
- [ ] Include equivalently transformed equations; verify answer options
- [ ] Add tests and a diagnostic explanation for each wrong choice

### Fernando — Algebraic Fractions
- [ ] Implement `algebraic_fractions.py` with safe nonzero denominators
- [ ] Add valid simplification and distractor checks
- [ ] Include misconceptions for common denominators and cancellation

### Sadeepa — Indices and Logarithms
- [ ] Implement `indices_logs.py` with domain-aware question validation
- [ ] Add exponent-law misconception categories
- [ ] Include domain restrictions in tests for logarithms

### Group agreement
- Use the same REST API and `TopicModule` interface for all topics.
- No module returns answer keys to students before submission.
- Peer-review generated mathematics and test each difficulty level.
- Build topic modules in feature branches, submit pull requests for integration.
- Do not use real children’s names or identifiable work in the local prototype.
