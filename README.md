# Simple 2D particle simulator

![](/home/ale/Pictures/markdown/2025-03-16T12:43:11,575036615-03:00.png)

Simulates randomly placed 2D disks and their interactions according to Newtonian physics. This is enough to observe some interesting behaviour, mainly orbits and small "solar systems". Collisions are handled by merging the particles, similar to how planets work.

To run on Linux clone the repo and inside do:

```
python3 -m venv venv
source ./venv/bin/activate.sh
pip install pygame
python3 sym.py
```

