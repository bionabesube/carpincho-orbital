# Carpincho Orbital — Mission Health Dashboard

Experimental web dashboard for longitudinal neuro-ophthalmic and physiological monitoring during space missions. The interface uses a dark, translucent mission-control visual language with cyan telemetry accents and orange mission markers. The original Carpincho Orbital team logo is retained.

> **Important:** all preloaded records are synthetic demo data. This prototype does not directly measure or estimate intracranial pressure (ICP), does not diagnose SANS, and must not be used for clinical decisions. The displayed measurements and screening protocols require appropriate validation.

## What is included

- Clinical-team dashboard and astronaut-facing view.
- Compact mission route timeline: Earth, Earth orbit, Mars, return orbit, and Earth recovery. The current Earth-orbit phase is illustrative demo state.
- Interactive anatomical locator that highlights the brain, eyes, optic pathway, or wrist according to the selected assessment category. It is an educational reference illustration, not a diagnostic image.
- Visual-field screening result maps, per-eye detection rates, missed stimuli, false positives, response times, quadrant summaries, and longitudinal comparison.
- Eye-tracking result display when a compatible headset sends processed gaze metrics: valid-sample percentage, gaze-on-target percentage, fixation dispersion, mean gaze error, blink count, and saccade count.
- Manual entry of basic assessments performed outside the headset: visual acuity, refraction (sphere/cylinder/axis), and near point.
- Astronaut symptom self-report and clinical follow-up scheduling.
- Wearable data history and CSV import.
- REST endpoints for Godot VR sessions, visual-field/eye-tracking results, and normalized wearable summaries.
- Local SQLite storage. The database is created automatically as `astrohealth.db`; PostgreSQL is not required for local development.

The dashboard distinguishes between tests performed in Godot/VR (visual field and eye tracking) and basic manual assessments performed outside the headset. The SVG illustrations in `app/static/exams/` are visual references only.

The Clinical Team / Astronaut switch changes the displayed view only. It does **not** implement authentication or production-grade access control. Do not enter personal information or real patient data.

## Requirements

- Python 3.11 or later recommended.
- Git is optional.

## Run locally

Open a terminal in this folder:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Linux/macOS:

```bash
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`.

- `/?role=clinician`: Clinical Team view.
- `/?role=astronaut`: Astronaut view.
- `/docs`: interactive API documentation.
- `/health`: service health check.

SQLite is created automatically. To reset the demo data, stop the server and remove `astrohealth.db`.

## Godot integration

Godot sends a JSON payload when a VR protocol is completed. The dashboard stores processed results; it does not run the visual-field test or process raw eye-camera data.

Example session endpoint:

```text
POST /api/v1/vr/sessions
Content-Type: application/json
X-API-Key: <VR_API_KEY>
```

Example visual field and eye-tracking endpoint:

```text
POST /api/v1/visual-field
Content-Type: application/json
X-API-Key: <VR_API_KEY>
```

One eye is submitted per visual-field payload. Send separate payloads for OD (right eye) and OS (left eye). The `eye_tracking` object should contain processed metrics and must be `null` or omitted when compatible eye-tracking hardware is unavailable. Do not infer gaze from headset position alone.

For eye tracking, document headset model, calibration procedure, sampling rate, coordinate system, validity criteria, and filtering. The dashboard can display these values but cannot validate the eye-tracking algorithm.

## Wearables

### Actiwatch Spectrum

The prototype path is to export data from Actiware to CSV and import the file in the Wearables section. Actual exports may require column mapping; confirm units, timestamps, aggregation, and sleep-scoring method for the specific export.

### Empatica EmbracePlus

Access depends on the account, platform permissions, and applicable Empatica service. If data are downloaded as Avro or CSV, inspect the schema and normalize timestamps, units, and signal names before importing. The supplied inspector script is in `integrations/inspect_empatica_avro.py` and requires `fastavro`.

### Smartwatches

A mobile application or approved health-data connector is needed to collect platform data. A browser dashboard alone cannot directly access private Apple Health or Android Health Connect data.

The `data/` folder contains synthetic CSV/JSON examples. They are not authentic device exports.

## Scientific scope and limitations

The VR visual-field grid is exploratory and is not equivalent to validated clinical perimetry. This prototype does not calculate MD, PSD, or VFI. It does not include OCT, MRI, ultrasound, or direct ICP measurement. Wearable signals provide context and are not direct measurements of intracranial pressure or a standalone SANS diagnosis.

The anatomical locator is a simplified visual aid highlighting the body region associated with the selected study. It does not show an individual astronaut's actual physiological state.

## Deployment

The included `render.yaml` is a starting point for Render. For a persistent deployment, configure a persistent disk for SQLite or move to a managed database later. A free ephemeral filesystem may be reset during redeploys or restarts. Configure `VR_API_KEY` using the hosting provider's secret/environment settings; do not commit a real key.

## Publish with GitHub + Render

The repository includes a `render.yaml` configured for a straightforward Render Free demo deployment.

1. Create a new empty repository on GitHub.
2. Extract this project and upload the **contents of this folder** (`app/`, `data/`, `integrations/`, `requirements.txt`, `render.yaml`, etc.) to the repository root. Do not upload the ZIP file itself.
3. In Render, choose **New + → Blueprint** (or create a **New Web Service** and connect the repository).
4. If using the Blueprint, Render reads `render.yaml`. If creating a Web Service manually, use:
   - Runtime: Python 3
   - Root Directory: leave blank when the project files are at the repository root
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Wait for deployment and open the `onrender.com` URL. Check `/health`; it should return `{"status":"ok", ...}`.
6. Render generates `VR_API_KEY` from `render.yaml`. Treat it as a secret. Copy it from the Render Environment page into the Godot project's secret/configuration; do not put it in GitHub or in client-side browser code.

### Important: database persistence on Render

The default `render.yaml` uses SQLite on the service filesystem so the demo is easy to deploy without PostgreSQL. **Render Free uses an ephemeral filesystem:** the demo database and any records added after startup can be lost when the service restarts or redeploys. Keep this deployment limited to synthetic demonstration data.

If you later need SQLite data to survive restarts and redeploys, use a Render plan that supports persistent disks and the optional `render-with-persistent-disk.yaml` configuration. It mounts a disk at `/var/data` and stores the SQLite file there. Persistent disks are a paid Render feature and constrain scaling to a single service instance. This is still SQLite; it does not require running PostgreSQL on your computer.

### Security before any real use

This prototype has no user login or role-based access control. The clinician/astronaut switch is only a view switch. Do not publish or enter real patient/astronaut health information. Keep using synthetic data until authentication, authorization, transport/security review, backup, and data-governance requirements are implemented.
