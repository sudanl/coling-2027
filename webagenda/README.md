## Generating the Schedule for the Website

This directory contains the data files and code used to generate the schedule for the COLING 2027 official website.

### Setting Up

```bash
conda create -n coling2027 -c conda-forge --file agenda/requirements.txt
conda activate coling2027
```

### Generating the Schedule

```
python webagenda/generate.py webagenda/config.json _pages/output/schedule.md
```

See `config.json` for configuration details.
