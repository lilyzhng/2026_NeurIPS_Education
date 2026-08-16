Speculative decoding now runs under nearly every hosted LLM, and the field reports success in acceptance rate and token speed while claiming the result is lossless. This education material is organized around three questions:

- <u>What's Measured</u>: how does speculative decoding work, and why is it lossless in theory?
- <u>What's Missed</u>: does lossless inference hold true beyond math and code?
- <u>What's Next</u>: who owns the quality of accelerated inference?

Learners walk through three generations of draft models: EAGLE-3, DFlash, DSpark. Token speed and acceptance rate get reported, mostly on math and code. What is missing is token quality, unmeasured everywhere else. A hands-on lab on a single GPU reproduces the numbers: serve an accelerated model, and grade the outputs.
