from __future__ import annotations

import csv
import io
import json
import os
import secrets
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from typing import Any, Optional

from fastapi import Depends, FastAPI, File, Form, Header, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text, create_engine, inspect, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, sessionmaker


# ---------------------------------------------------------------------------
# Configuration and database
# ---------------------------------------------------------------------------

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./astrohealth.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    callsign: Mapped[str] = mapped_column(String(100), default="Demo Astronaut")
    mission_phase: Mapped[str] = mapped_column(String(80), default="Earth orbit")
    mission_day: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    exams: Mapped[list["ClinicalExam"]] = relationship(back_populates="patient", cascade="all, delete-orphan")
    symptoms: Mapped[list["SymptomReport"]] = relationship(back_populates="patient", cascade="all, delete-orphan")
    wearables: Mapped[list["WearableDaily"]] = relationship(back_populates="patient", cascade="all, delete-orphan")
    followups: Mapped[list["FollowUp"]] = relationship(back_populates="patient", cascade="all, delete-orphan")
    vr_sessions: Mapped[list["VRSession"]] = relationship(back_populates="patient", cascade="all, delete-orphan")


class ClinicalExam(Base):
    __tablename__ = "clinical_exams"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    patient_id: Mapped[str] = mapped_column(ForeignKey("patients.id"), index=True)
    measured_at: Mapped[date] = mapped_column(Date, index=True)
    exam_type: Mapped[str] = mapped_column(String(80), default="Neuro-ophthalmic assessment")
    visual_acuity_right: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    visual_acuity_left: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    sphere_right: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sphere_left: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    cylinder_right: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    cylinder_left: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    axis_right: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    axis_left: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    near_point_cm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    clinician_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    patient: Mapped[Patient] = relationship(back_populates="exams")


class VisualFieldTest(Base):
    __tablename__ = "visual_field_tests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    patient_id: Mapped[str] = mapped_column(ForeignKey("patients.id"), index=True)
    tested_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    eye: Mapped[str] = mapped_column(String(2), index=True)  # OD or OI internally; displayed as OD or OS
    protocol_name: Mapped[str] = mapped_column(String(100), default="VR suprathreshold screening")
    protocol_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    stimulus_profile: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    total_points: Mapped[int] = mapped_column(Integer, default=0)
    seen_points: Mapped[int] = mapped_column(Integer, default=0)
    detection_pct: Mapped[float] = mapped_column(Float, default=0.0)
    false_positive_count: Mapped[int] = mapped_column(Integer, default=0)
    catch_trial_count: Mapped[int] = mapped_column(Integer, default=0)
    median_reaction_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    head_motion_events: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    eye_tracking_available: Mapped[bool] = mapped_column(Boolean, default=False)
    fixation_loss_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    eye_tracking_json: Mapped[str] = mapped_column(Text, default="{}")
    points_json: Mapped[str] = mapped_column(Text, default="[]")
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class SymptomReport(Base):
    __tablename__ = "symptom_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    patient_id: Mapped[str] = mapped_column(ForeignKey("patients.id"), index=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    headache_score: Mapped[int] = mapped_column(Integer, default=0)
    blurred_vision: Mapped[bool] = mapped_column(Boolean, default=False)
    double_vision: Mapped[bool] = mapped_column(Boolean, default=False)
    transient_visual_obscuration: Mapped[bool] = mapped_column(Boolean, default=False)
    pulsatile_tinnitus: Mapped[bool] = mapped_column(Boolean, default=False)
    nausea: Mapped[bool] = mapped_column(Boolean, default=False)
    dizziness: Mapped[bool] = mapped_column(Boolean, default=False)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    patient: Mapped[Patient] = relationship(back_populates="symptoms")


class WearableDaily(Base):
    __tablename__ = "wearable_daily"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    patient_id: Mapped[str] = mapped_column(ForeignKey("patients.id"), index=True)
    day: Mapped[date] = mapped_column(Date, index=True)
    source: Mapped[str] = mapped_column(String(80), default="Manual")
    sleep_hours: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    activity_count: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    steps: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    heart_rate_mean: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    heart_rate_resting: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    hrv_rmssd: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    skin_temp_c: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    eda_mean: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    light_lux: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sample_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    data_quality_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    patient: Mapped[Patient] = relationship(back_populates="wearables")


class FollowUp(Base):
    __tablename__ = "followups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    patient_id: Mapped[str] = mapped_column(ForeignKey("patients.id"), index=True)
    due_date: Mapped[date] = mapped_column(Date, index=True)
    category: Mapped[str] = mapped_column(String(100), default="Neuro-ophthalmic check-up")
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)

    patient: Mapped[Patient] = relationship(back_populates="followups")


class VRSession(Base):
    __tablename__ = "vr_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    patient_id: Mapped[str] = mapped_column(ForeignKey("patients.id"), index=True)
    session_id: Mapped[str] = mapped_column(String(100), index=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    protocol_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    task_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    metrics_json: Mapped[str] = mapped_column(Text, default="{}")
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    patient: Mapped[Patient] = relationship(back_populates="vr_sessions")


Base.metadata.create_all(bind=engine)
# Add columns to existing SQLite/PostgreSQL demo databases without requiring deletion.
with engine.begin() as connection:
    vf_columns = {column["name"] for column in inspect(connection).get_columns("visual_field_tests")}
    if "eye_tracking_json" not in vf_columns:
        connection.exec_driver_sql("ALTER TABLE visual_field_tests ADD COLUMN eye_tracking_json TEXT NOT NULL DEFAULT '{}'")
    exam_columns = {column["name"] for column in inspect(connection).get_columns("clinical_exams")}
    if "near_point_cm" not in exam_columns:
        connection.exec_driver_sql("ALTER TABLE clinical_exams ADD COLUMN near_point_cm FLOAT")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Demo data. All values are fictional and are only for demonstrating the UI.
# ---------------------------------------------------------------------------

def seed_demo_data() -> None:
    with SessionLocal() as db:
        patient = db.get(Patient, "ASTRO-DEMO-01")
        if patient:
            return
        patient = Patient(
            id="ASTRO-DEMO-01",
            callsign="Demo Astronaut",
            mission_phase="Earth orbit",
            mission_day=14,
        )
        db.add(patient)
        today = date.today()
        for offset, sphere in enumerate([0.25, 0.25, 0.50, 0.50]):
            db.add(ClinicalExam(
                patient_id=patient.id,
                measured_at=today - timedelta(days=45 - offset * 10),
                exam_type="Visual acuity + refraction",
                visual_acuity_right="20/20",
                visual_acuity_left="20/20",
                sphere_right=sphere,
                sphere_left=sphere + 0.25,
                cylinder_right=-0.25,
                cylinder_left=-0.25,
                near_point_cm=8.5 + offset * 0.2,
                clinician_note="Synthetic demonstration result; not associated with a real person."
            ))

        # Points for a custom exploratory grid. It is not equivalent to 24-2/30-2 or validated clinical perimetry.
        vf_coords = [(x, y) for y in (-12, -6, 0, 6, 12) for x in (-18, -12, -6, 6, 12, 18)]
        for eye, miss_counts in (("OD", [1, 2, 4]), ("OI", [0, 1, 1])):
            for idx, miss_n in enumerate(miss_counts):
                points = []
                # Place a few missed points in the temporal field for a visible demo pattern only.
                miss_candidates = [(12, 0), (18, 0), (12, 6), (18, -6)]
                missed = set(miss_candidates[:miss_n])
                for x, y in vf_coords:
                    points.append({"x_deg": x, "y_deg": y, "seen": (x, y) not in missed, "reaction_time_ms": 390 + ((x + y + 30) % 7) * 11 if (x, y) not in missed else None})
                seen = sum(1 for p in points if p["seen"])
                reaction = [p["reaction_time_ms"] for p in points if p["reaction_time_ms"] is not None]
                db.add(VisualFieldTest(
                    patient_id=patient.id,
                    tested_at=datetime.combine(today - timedelta(days=40 - idx * 19), datetime.min.time()) + timedelta(hours=12),
                    eye=eye,
                    protocol_name="Exploratory VR grid",
                    protocol_version="0.2-demo",
                    stimulus_profile="Fixed brightness · uncalibrated demo profile",
                    total_points=len(points),
                    seen_points=seen,
                    detection_pct=round(seen / len(points) * 100, 1),
                    false_positive_count=0 if idx < 2 else 1,
                    catch_trial_count=4,
                    median_reaction_ms=round(sorted(reaction)[len(reaction)//2], 1),
                    head_motion_events=0 if idx == 0 else 1,
                    eye_tracking_available=True,
                    fixation_loss_pct=round(3.0 + idx * 0.8, 1),
                    eye_tracking_json=json.dumps({
                        "tracking_valid_pct": round(97.5 - idx * 1.4, 1),
                        "gaze_on_target_pct": round(94.0 - idx * 1.8, 1),
                        "fixation_dispersion_deg": round(0.85 + idx * 0.14, 2),
                        "mean_gaze_error_deg": round(0.62 + idx * 0.12, 2),
                        "blink_count": 12 + idx * 2,
                        "saccade_count": 35 + idx * 3,
                        "sample_count": 1800 + idx * 60
                    }),
                    points_json=json.dumps(points),
                    notes="Synthetic demonstration data. Not a real measurement or clinical finding."
                ))
        db.add(SymptomReport(
            patient_id=patient.id,
            recorded_at=datetime.utcnow() - timedelta(hours=9),
            headache_score=1,
            blurred_vision=False,
            comment="Synthetic demo report. Not associated with a real person.",
        ))
        for n in range(14):
            d = today - timedelta(days=13 - n)
            db.add(WearableDaily(
                patient_id=patient.id,
                day=d,
                source="Synthetic demo data",
                sleep_hours=round(7.0 + ((n % 5) - 2) * 0.25, 1),
                activity_count=round(420 + (n % 4) * 35, 1),
                steps=5800 + n * 110,
                heart_rate_mean=68 + (n % 4),
                heart_rate_resting=57 + (n % 3),
                hrv_rmssd=42 + (n % 5),
                skin_temp_c=33.1 + (n % 3) * 0.1,
                eda_mean=0.8 + (n % 4) * 0.05,
                light_lux=110 + n * 3,
                sample_count=1440,
                data_quality_note="Synthetic demonstration data",
            ))
        db.add(FollowUp(
            patient_id=patient.id,
            due_date=today + timedelta(days=7),
            category="Neuro-ophthalmic check-up",
            notes="Illustrative date for the prototype",
        ))
        db.add(VRSession(
            patient_id=patient.id,
            session_id="VR-DEMO-001",
            completed_at=datetime.utcnow() - timedelta(days=2),
            protocol_version="0.1-demo",
            task_name="Visual and oculomotor assessment",
            metrics_json=json.dumps({"reaction_time_ms": 420, "task_accuracy_pct": 96, "completed_tasks": 5}),
            notes="Simulated metrics; protocol validation required.",
        ))
        db.commit()


seed_demo_data()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def latest_or_none(items: list[Any]) -> Any | None:
    return items[0] if items else None


def as_float(value: Any) -> Optional[float]:
    if value is None or str(value).strip() == "":
        return None
    try:
        return float(str(value).strip().replace(",", "."))
    except (TypeError, ValueError):
        return None


def as_int(value: Any) -> Optional[int]:
    if value is None or str(value).strip() == "":
        return None
    try:
        return int(float(str(value).strip().replace(",", ".")))
    except (TypeError, ValueError):
        return None


def parse_datetime(value: Any) -> Optional[datetime]:
    if value is None or str(value).strip() == "":
        return None
    raw = str(value).strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d", "%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M", "%d/%m/%Y"):
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            pass
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError:
        return None


def parse_date(value: Any) -> Optional[date]:
    parsed = parse_datetime(value)
    return parsed.date() if parsed else None


def get_column(row: dict[str, Any], aliases: tuple[str, ...]) -> Any:
    normalized = {str(k).strip().lower().replace(" ", "_").replace("-", "_"): v for k, v in row.items() if k}
    for alias in aliases:
        key = alias.lower().replace(" ", "_").replace("-", "_")
        if key in normalized and normalized[key] not in (None, ""):
            return normalized[key]
    return None


def patient_or_404(db: Session, patient_id: str) -> Patient:
    patient = db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Astronaut not found")
    return patient


def verify_vr_key(x_api_key: Optional[str]) -> None:
    expected = os.getenv("VR_API_KEY")
    if expected and (not x_api_key or not secrets.compare_digest(x_api_key, expected)):
        raise HTTPException(status_code=401, detail="API key is invalid or missing")


# ---------------------------------------------------------------------------
# API schemas and app
# ---------------------------------------------------------------------------

class VRSessionPayload(BaseModel):
    model_config = ConfigDict(extra="allow")

    astronaut_id: str = Field(min_length=1, max_length=40)
    session_id: str = Field(min_length=1, max_length=100)
    completed_at: Optional[datetime] = None
    protocol_version: Optional[str] = None
    task_name: Optional[str] = None
    metrics: dict[str, Any] = Field(default_factory=dict)
    notes: Optional[str] = None


class VisualFieldPointPayload(BaseModel):
    x_deg: float = Field(ge=-40, le=40)
    y_deg: float = Field(ge=-40, le=40)
    seen: bool
    reaction_time_ms: Optional[float] = Field(default=None, ge=0, le=30000)


class EyeTrackingMetrics(BaseModel):
    """Optional gaze metrics produced by the headset's eye-tracking pipeline."""
    tracking_valid_pct: Optional[float] = Field(default=None, ge=0, le=100)
    gaze_on_target_pct: Optional[float] = Field(default=None, ge=0, le=100)
    fixation_dispersion_deg: Optional[float] = Field(default=None, ge=0, le=90)
    mean_gaze_error_deg: Optional[float] = Field(default=None, ge=0, le=90)
    blink_count: Optional[int] = Field(default=None, ge=0)
    saccade_count: Optional[int] = Field(default=None, ge=0)
    sample_count: Optional[int] = Field(default=None, ge=0)


class VisualFieldPayload(BaseModel):
    astronaut_id: str = Field(min_length=1, max_length=40)
    session_id: str = Field(min_length=1, max_length=100)
    tested_at: Optional[datetime] = None
    eye: str = Field(pattern="^(OD|OI|OS)$")
    protocol_name: str = "VR suprathreshold screening"
    protocol_version: Optional[str] = None
    stimulus_profile: Optional[str] = None
    points: list[VisualFieldPointPayload] = Field(min_length=1, max_length=500)
    catch_trial_count: int = Field(default=0, ge=0, le=500)
    false_positive_count: int = Field(default=0, ge=0, le=500)
    head_motion_events: Optional[int] = Field(default=None, ge=0)
    eye_tracking_available: bool = False
    fixation_loss_pct: Optional[float] = Field(default=None, ge=0, le=100)
    eye_tracking: Optional[EyeTrackingMetrics] = None
    notes: Optional[str] = None


class WearableDailyPayload(BaseModel):
    astronaut_id: str
    day: date
    source: str = "API"
    sleep_hours: Optional[float] = None
    activity_count: Optional[float] = None
    steps: Optional[int] = None
    heart_rate_mean: Optional[float] = None
    heart_rate_resting: Optional[float] = None
    hrv_rmssd: Optional[float] = None
    skin_temp_c: Optional[float] = None
    eda_mean: Optional[float] = None
    light_lux: Optional[float] = None
    sample_count: Optional[int] = None


app = FastAPI(title="Carpincho Orbital | Mission Health Operations", version="0.4.0")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "Carpincho Orbital Mission Health Operations", "version": "0.4.0"}


@app.get("/api/v1/patients/{patient_id}/timeline")
def patient_timeline(patient_id: str, db: Session = Depends(get_db)):
    patient_or_404(db, patient_id)
    exams = db.scalars(select(ClinicalExam).where(ClinicalExam.patient_id == patient_id).order_by(ClinicalExam.measured_at)).all()
    wearables = db.scalars(select(WearableDaily).where(WearableDaily.patient_id == patient_id).order_by(WearableDaily.day)).all()
    return {
        "astronaut_id": patient_id,
        "clinical_exams": [{"date": x.measured_at.isoformat(), "exam_type": x.exam_type, "visual_acuity_right": x.visual_acuity_right, "visual_acuity_left": x.visual_acuity_left, "sphere_right_diopters": x.sphere_right, "sphere_left_diopters": x.sphere_left, "near_point_cm": x.near_point_cm} for x in exams],
        "visual_field": [{"date": x.tested_at.isoformat(), "eye": ("OS" if x.eye == "OI" else "OD"), "detection_pct": x.detection_pct, "missed_points": x.total_points - x.seen_points, "total_points": x.total_points} for x in db.scalars(select(VisualFieldTest).where(VisualFieldTest.patient_id == patient_id).order_by(VisualFieldTest.tested_at)).all()],
        "wearables_daily": [{"date": x.day.isoformat(), "source": x.source, "sleep_hours": x.sleep_hours, "activity_count": x.activity_count, "steps": x.steps, "heart_rate_mean": x.heart_rate_mean, "hrv_rmssd": x.hrv_rmssd} for x in wearables],
    }


@app.post("/api/v1/vr/sessions")
def ingest_vr_session(
    payload: VRSessionPayload,
    x_api_key: Optional[str] = Header(default=None),
    db: Session = Depends(get_db),
):
    """Receives a completed Godot VR assessment. Metrics are stored, not diagnosed."""
    verify_vr_key(x_api_key)
    patient_or_404(db, payload.astronaut_id)
    completed = payload.completed_at
    if completed and completed.tzinfo:
        completed = completed.astimezone(timezone.utc).replace(tzinfo=None)
    db.add(VRSession(
        patient_id=payload.astronaut_id,
        session_id=payload.session_id,
        completed_at=completed or datetime.utcnow(),
        protocol_version=payload.protocol_version,
        task_name=payload.task_name,
        metrics_json=json.dumps(payload.metrics, ensure_ascii=False),
        notes=payload.notes,
    ))
    db.commit()
    return {"accepted": True, "session_id": payload.session_id, "stored_metrics": list(payload.metrics.keys())}


@app.post("/api/v1/visual-field")
def ingest_visual_field(
    payload: VisualFieldPayload,
    x_api_key: Optional[str] = Header(default=None),
    db: Session = Depends(get_db),
):
    """Store per-point VR visual-field screening outcomes. Does not calculate clinical perimetry indices."""
    verify_vr_key(x_api_key)
    patient_or_404(db, payload.astronaut_id)
    points = [p.model_dump() for p in payload.points]
    total = len(points)
    seen = sum(1 for p in points if p["seen"])
    reaction_times = sorted(p["reaction_time_ms"] for p in points if p.get("reaction_time_ms") is not None and p["seen"])
    median_rt = None if not reaction_times else float(reaction_times[len(reaction_times)//2])
    tested_at = payload.tested_at or datetime.utcnow()
    if tested_at.tzinfo:
        tested_at = tested_at.astimezone(timezone.utc).replace(tzinfo=None)
    record = VisualFieldTest(
        patient_id=payload.astronaut_id, tested_at=tested_at, eye=("OI" if payload.eye == "OS" else payload.eye),
        protocol_name=payload.protocol_name[:100], protocol_version=payload.protocol_version,
        stimulus_profile=payload.stimulus_profile, total_points=total, seen_points=seen,
        detection_pct=round(seen / total * 100, 1),
        false_positive_count=payload.false_positive_count, catch_trial_count=payload.catch_trial_count,
        median_reaction_ms=median_rt, head_motion_events=payload.head_motion_events,
        eye_tracking_available=payload.eye_tracking_available or payload.eye_tracking is not None, fixation_loss_pct=payload.fixation_loss_pct,
        eye_tracking_json=json.dumps(payload.eye_tracking.model_dump(exclude_none=True) if payload.eye_tracking else {}, ensure_ascii=False),
        points_json=json.dumps(points, ensure_ascii=False), notes=payload.notes
    )
    db.add(record)
    db.commit()
    return {
        "accepted": True, "session_id": payload.session_id, "eye": ("OS" if payload.eye in ("OI", "OS") else "OD"),
        "total_points": total, "seen_points": seen, "missed_points": total - seen,
        "detection_pct": record.detection_pct, "median_reaction_ms": median_rt,
        "eye_tracking": payload.eye_tracking.model_dump(exclude_none=True) if payload.eye_tracking else None,
        "message": "Stored as exploratory VR screening; no clinical MD/PSD/VFI indices were calculated."
    }


@app.get("/api/v1/patients/{patient_id}/visual-field")
def get_visual_field_history(patient_id: str, db: Session = Depends(get_db)):
    patient_or_404(db, patient_id)
    tests = db.scalars(select(VisualFieldTest).where(VisualFieldTest.patient_id == patient_id).order_by(VisualFieldTest.tested_at)).all()
    return [{
        "tested_at": x.tested_at.isoformat(), "eye": x.eye, "protocol_name": x.protocol_name,
        "total_points": x.total_points, "seen_points": x.seen_points,
        "missed_points": x.total_points - x.seen_points, "detection_pct": x.detection_pct,
        "false_positive_count": x.false_positive_count, "catch_trial_count": x.catch_trial_count,
        "median_reaction_ms": x.median_reaction_ms, "eye_tracking_available": x.eye_tracking_available,
        "fixation_loss_pct": x.fixation_loss_pct, "eye_tracking": json.loads(x.eye_tracking_json or "{}"), "points": json.loads(x.points_json)
    } for x in tests]


@app.post("/api/v1/wearables/daily")
def ingest_wearable_daily(payload: WearableDailyPayload, db: Session = Depends(get_db)):
    """Normalized wearable summary endpoint. Protect this endpoint before real deployment."""
    patient_or_404(db, payload.astronaut_id)
    db.add(WearableDaily(
        patient_id=payload.astronaut_id,
        day=payload.day,
        source=payload.source,
        sleep_hours=payload.sleep_hours,
        activity_count=payload.activity_count,
        steps=payload.steps,
        heart_rate_mean=payload.heart_rate_mean,
        heart_rate_resting=payload.heart_rate_resting,
        hrv_rmssd=payload.hrv_rmssd,
        skin_temp_c=payload.skin_temp_c,
        eda_mean=payload.eda_mean,
        light_lux=payload.light_lux,
        sample_count=payload.sample_count,
    ))
    db.commit()
    return {"accepted": True, "astronaut_id": payload.astronaut_id, "day": payload.day.isoformat()}


# ---------------------------------------------------------------------------
# Web dashboard
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, role: str = "clinician", db: Session = Depends(get_db)):
    patient = patient_or_404(db, "ASTRO-DEMO-01")
    exams = db.scalars(select(ClinicalExam).where(ClinicalExam.patient_id == patient.id).order_by(ClinicalExam.measured_at.desc())).all()
    symptoms = db.scalars(select(SymptomReport).where(SymptomReport.patient_id == patient.id).order_by(SymptomReport.recorded_at.desc())).all()
    wearables = db.scalars(select(WearableDaily).where(WearableDaily.patient_id == patient.id).order_by(WearableDaily.day.desc())).all()
    followups = db.scalars(select(FollowUp).where(FollowUp.patient_id == patient.id).order_by(FollowUp.due_date.asc())).all()
    vr_sessions = db.scalars(select(VRSession).where(VRSession.patient_id == patient.id).order_by(VRSession.completed_at.desc())).all()
    visual_field_tests = db.scalars(select(VisualFieldTest).where(VisualFieldTest.patient_id == patient.id).order_by(VisualFieldTest.tested_at.desc())).all()

    latest_exam = latest_or_none(exams)
    latest_symptom = latest_or_none(symptoms)
    latest_wearable = latest_or_none(wearables)
    next_followup = next((f for f in followups if not f.completed and f.due_date >= date.today()), None)

    wearable_chart = sorted(wearables, key=lambda x: x.day)
    vf_chart = sorted(visual_field_tests, key=lambda x: x.tested_at)
    vf_labels = [x.tested_at.strftime("%d/%m") for x in vf_chart]
    vf_od = [x.detection_pct if x.eye == "OD" else None for x in vf_chart]
    vf_oi = [x.detection_pct if x.eye == "OI" else None for x in vf_chart]
    wearable_labels = [x.day.strftime("%d/%m") for x in wearable_chart]
    sleep_hours = [x.sleep_hours for x in wearable_chart]
    hr_resting = [x.heart_rate_resting for x in wearable_chart]

    latest_vf_od = next((x for x in visual_field_tests if x.eye == "OD"), None)
    latest_vf_oi = next((x for x in visual_field_tests if x.eye == "OI"), None)

    def map_points(test):
        if not test:
            return []
        mapped = []
        for point in json.loads(test.points_json):
            x = float(point.get("x_deg", 0))
            y = float(point.get("y_deg", 0))
            mapped.append({
                "cx": round(130 + x * 4), "cy": round(115 - y * 4),
                "seen": bool(point.get("seen", False)),
                "x_deg": x, "y_deg": y,
            })
        return mapped

    def region_stats(test):
        if not test:
            return []
        points = json.loads(test.points_json)
        regions = [
            ("Superior nasal", lambda x, y: x < 0 and y > 0),
            ("Superior temporal", lambda x, y: x > 0 and y > 0),
            ("Inferior nasal", lambda x, y: x < 0 and y < 0),
            ("Inferior temporal", lambda x, y: x > 0 and y < 0),
        ]
        output = []
        for label, predicate in regions:
            subset = [p for p in points if predicate(float(p.get("x_deg", 0)), float(p.get("y_deg", 0)))]
            if subset:
                seen_count = sum(1 for p in subset if p.get("seen"))
                output.append({"label": label, "seen": seen_count, "total": len(subset), "pct": round(seen_count / len(subset) * 100, 1)})
        return output

    def tracking_metrics(test):
        if not test or not test.eye_tracking_available:
            return {}
        try:
            return json.loads(test.eye_tracking_json or "{}")
        except (TypeError, json.JSONDecodeError):
            return {}

    def baseline_delta(test):
        if not test:
            return None
        history = sorted([x for x in visual_field_tests if x.eye == test.eye], key=lambda x: x.tested_at)
        if len(history) < 2:
            return None
        baseline = history[0]
        if (baseline.protocol_name, baseline.protocol_version, baseline.stimulus_profile) != (test.protocol_name, test.protocol_version, test.stimulus_profile):
            return None
        return round(test.detection_pct - baseline.detection_pct, 1)

    mission_phase_value = (patient.mission_phase or "").strip().lower()
    if any(token in mission_phase_value for token in ("re-entry", "reentry", "recovery", "post-flight", "returned")):
        mission_stage = 4
    elif "return" in mission_phase_value:
        mission_stage = 3
    elif "mars" in mission_phase_value:
        mission_stage = 2
    elif "orbit" in mission_phase_value:
        mission_stage = 1
    else:
        mission_stage = 0
    mission_stage_labels = ["EARTH / PRE-LAUNCH", "EARTH ORBIT", "MARS OPERATIONS", "RETURN ORBIT", "EARTH / RECOVERY"]
    mission_stage_label = mission_stage_labels[mission_stage]
    mission_progress_pct = mission_stage * 20

    context = {
        "request": request,
        "mission_stage": mission_stage,
        "mission_stage_label": mission_stage_label,
        "mission_progress_pct": mission_progress_pct,
        "role": role if role in ("clinician", "astronaut") else "clinician",
        "patient": patient,
        "exams": exams,
        "symptoms": symptoms,
        "wearables": wearables,
        "followups": followups,
        "vr_sessions": vr_sessions,
        "visual_field_tests": visual_field_tests,
        "latest_vf_od": latest_vf_od,
        "latest_vf_oi": latest_vf_oi,
        "vf_od_points": map_points(latest_vf_od),
        "vf_oi_points": map_points(latest_vf_oi),
        "vf_od_regions": region_stats(latest_vf_od),
        "vf_oi_regions": region_stats(latest_vf_oi),
        "vf_od_delta": baseline_delta(latest_vf_od),
        "vf_oi_delta": baseline_delta(latest_vf_oi),
        "vf_od_tracking": tracking_metrics(latest_vf_od),
        "vf_oi_tracking": tracking_metrics(latest_vf_oi),
        "latest_exam": latest_exam,
        "latest_symptom": latest_symptom,
        "latest_wearable": latest_wearable,
        "next_followup": next_followup,
        "vf_labels": json.dumps(vf_labels),
        "vf_od": json.dumps(vf_od),
        "vf_oi": json.dumps(vf_oi),
        "wearable_labels": json.dumps(wearable_labels),
        "sleep_hours": json.dumps(sleep_hours),
        "hr_resting": json.dumps(hr_resting),
    }
    return templates.TemplateResponse("dashboard.html", context)


@app.post("/symptoms")
def add_symptom(
    headache_score: int = Form(0),
    blurred_vision: Optional[str] = Form(None),
    double_vision: Optional[str] = Form(None),
    transient_visual_obscuration: Optional[str] = Form(None),
    pulsatile_tinnitus: Optional[str] = Form(None),
    nausea: Optional[str] = Form(None),
    dizziness: Optional[str] = Form(None),
    comment: str = Form(""),
    db: Session = Depends(get_db),
):
    headache_score = max(0, min(10, headache_score))
    db.add(SymptomReport(
        patient_id="ASTRO-DEMO-01",
        headache_score=headache_score,
        blurred_vision=bool(blurred_vision),
        double_vision=bool(double_vision),
        transient_visual_obscuration=bool(transient_visual_obscuration),
        pulsatile_tinnitus=bool(pulsatile_tinnitus),
        nausea=bool(nausea),
        dizziness=bool(dizziness),
        comment=comment.strip() or None,
    ))
    db.commit()
    return RedirectResponse(url="/?role=astronaut#symptoms", status_code=303)


@app.post("/exams")
def add_exam(
    measured_at: date = Form(...),
    exam_type: str = Form("Neuro-ophthalmic assessment"),
    visual_acuity_right: str = Form(""),
    visual_acuity_left: str = Form(""),
    sphere_right: str = Form(""),
    sphere_left: str = Form(""),
    cylinder_right: str = Form(""),
    cylinder_left: str = Form(""),
    axis_right: str = Form(""),
    axis_left: str = Form(""),
    near_point_cm: str = Form(""),
    clinician_note: str = Form(""),
    db: Session = Depends(get_db),
):
    db.add(ClinicalExam(
        patient_id="ASTRO-DEMO-01",
        measured_at=measured_at,
        exam_type=exam_type.strip() or "Neuro-ophthalmic assessment",
        visual_acuity_right=visual_acuity_right.strip() or None,
        visual_acuity_left=visual_acuity_left.strip() or None,
        sphere_right=as_float(sphere_right),
        sphere_left=as_float(sphere_left),
        cylinder_right=as_float(cylinder_right),
        cylinder_left=as_float(cylinder_left),
        axis_right=as_int(axis_right),
        axis_left=as_int(axis_left),
        near_point_cm=as_float(near_point_cm),
        clinician_note=clinician_note.strip() or None,
    ))
    db.commit()
    return RedirectResponse(url="/?role=clinician#clinical-data", status_code=303)


@app.post("/followups")
def add_followup(
    due_date: date = Form(...),
    category: str = Form("Neuro-ophthalmic check-up"),
    notes: str = Form(""),
    db: Session = Depends(get_db),
):
    db.add(FollowUp(patient_id="ASTRO-DEMO-01", due_date=due_date, category=category.strip(), notes=notes.strip() or None))
    db.commit()
    return RedirectResponse(url="/?role=clinician#followups", status_code=303)


@app.post("/wearables/upload")
async def upload_wearable_csv(
    file: UploadFile = File(...),
    source: str = Form("Actiwatch / CSV"),
    db: Session = Depends(get_db),
):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Upload a .csv file")
    raw = await file.read()
    if len(raw) > 8 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File exceeds the 8 MB limit")
    decoded = None
    for encoding in ("utf-8-sig", "latin-1"):
        try:
            decoded = raw.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    if decoded is None:
        raise HTTPException(status_code=400, detail="No se pudo leer el CSV. Guardalo como UTF-8.")

    reader = csv.DictReader(io.StringIO(decoded))
    if not reader.fieldnames:
        raise HTTPException(status_code=400, detail="El CSV no tiene encabezados reconocibles")

    daily: dict[date, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for row in reader:
        raw_date = get_column(row, ("date", "datetime", "timestamp", "start_time", "time"))
        day = parse_date(raw_date)
        if not day:
            continue
        mappings = {
            "sleep_hours": ("sleep_hours", "sleep_duration_hours"),
            "activity_count": ("activity", "activity_count", "activity_counts", "activity_score"),
            "steps": ("steps", "step_count"),
            "heart_rate_mean": ("heart_rate_mean", "heart_rate", "hr", "bpm"),
            "heart_rate_resting": ("heart_rate_resting", "resting_hr", "resting_heart_rate"),
            "hrv_rmssd": ("hrv_rmssd", "rmssd", "hrv"),
            "skin_temp_c": ("skin_temp_c", "skin_temperature", "temperature"),
            "eda_mean": ("eda_mean", "eda", "electrodermal_activity"),
            "light_lux": ("light_lux", "light", "lux", "white_light"),
        }
        for metric, aliases in mappings.items():
            value = as_float(get_column(row, aliases))
            if value is not None:
                daily[day][metric].append(value)

    if not daily:
        raise HTTPException(
            status_code=400,
            detail="No valid dates found. The CSV must include a Date, DateTime, or Timestamp column.",
        )

    inserted = 0
    for day, metrics in daily.items():
        def avg(name: str) -> Optional[float]:
            vals = metrics.get(name, [])
            return round(sum(vals) / len(vals), 3) if vals else None

        db.add(WearableDaily(
            patient_id="ASTRO-DEMO-01",
            day=day,
            source=source[:80],
            sleep_hours=avg("sleep_hours"),
            activity_count=sum(metrics["activity_count"]) if metrics.get("activity_count") else None,
            steps=int(sum(metrics["steps"])) if metrics.get("steps") else None,
            heart_rate_mean=avg("heart_rate_mean"),
            heart_rate_resting=avg("heart_rate_resting"),
            hrv_rmssd=avg("hrv_rmssd"),
            skin_temp_c=avg("skin_temp_c"),
            eda_mean=avg("eda_mean"),
            light_lux=avg("light_lux"),
            sample_count=max((len(v) for v in metrics.values()), default=None),
            data_quality_note="Imported from CSV; review units and aggregation algorithm.",
        ))
        inserted += 1
    db.commit()
    return RedirectResponse(url=f"/?role=clinician&imported={inserted}#wearables", status_code=303)


@app.post("/followups/{followup_id}/complete")
def complete_followup(followup_id: int, db: Session = Depends(get_db)):
    followup = db.get(FollowUp, followup_id)
    if not followup:
        raise HTTPException(status_code=404, detail="Check-up not found")
    followup.completed = True
    db.commit()
    return RedirectResponse(url="/?role=clinician#followups", status_code=303)
