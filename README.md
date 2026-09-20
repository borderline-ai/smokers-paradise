# Smokers Paradise

Shop app for Smokers Paradise, Nogales AZ. Built by BorderLine AI.

Live: https://borderline-ai.github.io/smokers-paradise

Open `CLAUDE.md` first. It explains how the codebase works, the constraints,
and what needs building next (a backend — nothing transactional works without
one, and that is proven in there, not guessed).

Quick start:

    cp app/index.html app/index.before171.html
    python3 stages/s171_yourchange.py
    python3 test/member.py && python3 test/counter.py

The app is one HTML file with no build step. Open it in a browser.
