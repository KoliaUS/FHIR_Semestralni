# Importování potřebných knihoven a modulů
from datetime import datetime, date
from decimal import Decimal
from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from fhir.resources.patient import Patient as FHIRPatient
from fhir.resources.humanname import HumanName
from fhir.resources.contactpoint import ContactPoint
from fhir.resources.address import Address
from fhir.resources.observation import Observation
from fhir.resources.bundle import Bundle
from fhir.resources.bundle import BundleEntry
import json

# Definice Flask aplikace
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializace SQLAlchemy s Flask aplikací
db = SQLAlchemy(app)

# Definice databázových modelů
class Patient(db.Model):
    __tablename__ = 'patients'
    patient_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    address = db.Column(db.String(255))
    phone = db.Column(db.String(20))

class Doctor(db.Model):
    __tablename__ = 'doctors'
    doctor_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    specialty = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100), unique=True, nullable=False)

class Pulse(db.Model):
    __tablename__ = 'pulse'
    pulse_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.patient_id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.doctor_id'), nullable=False)
    measurement_date = db.Column(db.DateTime, nullable=False)
    presence = db.Column(db.Boolean)
    rate = db.Column(db.Integer)
    regularity = db.Column(db.String(20))
    irregular_type = db.Column(db.String(50))
    character = db.Column(db.String(255))
    clinical_description = db.Column(db.Text)
    
    patient = db.relationship('Patient', backref=db.backref('pulse_measurements', lazy=True))
    doctor = db.relationship('Doctor', backref=db.backref('pulse_measurements', lazy=True))

class BloodPressure(db.Model):
    __tablename__ = 'blood_pressure'
    bp_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.patient_id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.doctor_id'), nullable=False)
    measurement_date = db.Column(db.DateTime, nullable=False)
    systolic = db.Column(db.Integer)
    diastolic = db.Column(db.Integer)
    mean_arterial_pressure = db.Column(db.Integer)
    pulse_pressure = db.Column(db.Integer)
    clinical_interpretation = db.Column(db.Text)
    
    patient = db.relationship('Patient', backref=db.backref('bp_measurements', lazy=True))
    doctor = db.relationship('Doctor', backref=db.backref('bp_measurements', lazy=True))

class BodyTemperature(db.Model):
    __tablename__ = 'body_temperature'
    temperature_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.patient_id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.doctor_id'), nullable=False)
    measurement_date = db.Column(db.DateTime, nullable=False)
    temperature = db.Column(db.Numeric(4, 1))
    body_exposure = db.Column(db.String(50))
    thermal_stress = db.Column(db.Text)
    menstrual_cycle_day = db.Column(db.Integer)
    confounding_factors = db.Column(db.Text)
    environmental_conditions = db.Column(db.Text)
    
    patient = db.relationship('Patient', backref=db.backref('temperature_measurements', lazy=True))
    doctor = db.relationship('Doctor', backref=db.backref('temperature_measurements', lazy=True))

class PulseOximetry(db.Model):
    __tablename__ = 'pulse_oximetry'
    oximetry_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.patient_id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.doctor_id'), nullable=False)
    measurement_date = db.Column(db.DateTime, nullable=False)
    spo2 = db.Column(db.Numeric(5, 2))
    spoc = db.Column(db.Numeric(5, 2))
    spco = db.Column(db.Numeric(5, 2))
    spmet = db.Column(db.Numeric(5, 2))
    waveform = db.Column(db.Text)
    interpretation = db.Column(db.Text)
    
    patient = db.relationship('Patient', backref=db.backref('oximetry_measurements', lazy=True))
    doctor = db.relationship('Doctor', backref=db.backref('oximetry_measurements', lazy=True))

class Respiration(db.Model):
    __tablename__ = 'respiration'
    respiration_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.patient_id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.doctor_id'), nullable=False)
    measurement_date = db.Column(db.DateTime, nullable=False)
    presence = db.Column(db.Boolean)
    rate = db.Column(db.Integer)
    regularity = db.Column(db.String(20))
    depth = db.Column(db.String(20))
    clinical_description = db.Column(db.Text)
    clinical_interpretation = db.Column(db.Text)
    
    patient = db.relationship('Patient', backref=db.backref('respiration_measurements', lazy=True))
    doctor = db.relationship('Doctor', backref=db.backref('respiration_measurements', lazy=True))

# Pomocné funkce pro převod dat do formátu FHIR
def convert_patient_to_fhir(patient):
    fhir_patient = FHIRPatient(
        id=str(patient.patient_id),
        name=[HumanName(given=[patient.first_name], family=patient.last_name)],
        gender=patient.gender,
        birthDate=patient.birth_date.isoformat(),
        address=[Address(text=patient.address)],
        telecom=[ContactPoint(system='phone', value=patient.phone)]
    )
    return fhir_patient

def convert_pulse_to_fhir(pulse):
    fhir_pulse = Observation(
        id=str(pulse.pulse_id),
        status='final',
        category=[{
            'coding': [{
                'system': 'http://terminology.hl7.org/CodeSystem/observation-category',
                'code': 'vital-signs',
                'display': 'Vital Signs'
            }]
        }],
        code={
            'coding': [{
                'system': 'http://loinc.org',
                'code': '8867-4',
                'display': 'Heart rate'
            }]
        },
        subject={'reference': f'Patient/{pulse.patient_id}'},
        effectiveDateTime=pulse.measurement_date.isoformat(),
        valueQuantity={
            'value': pulse.rate,
            'unit': 'beats/minute',
            'system': 'http://unitsofmeasure.org',
            'code': '/min'
        }
    )
    return fhir_pulse

def convert_blood_pressure_to_fhir(bp):
    fhir_bp = Observation(
        id=str(bp.bp_id),
        status='final',
        category=[{
            'coding': [{
                'system': 'http://terminology.hl7.org/CodeSystem/observation-category',
                'code': 'vital-signs',
                'display': 'Vital Signs'
            }]
        }],
        code={
            'coding': [{
                'system': 'http://loinc.org',
                'code': '85354-9',
                'display': 'Blood pressure panel with all children optional'
            }]
        },
        subject={'reference': f'Patient/{bp.patient_id}'},
        effectiveDateTime=bp.measurement_date.isoformat(),
        component=[
            {
                'code': {
                    'coding': [{
                        'system': 'http://loinc.org',
                        'code': '8480-6',
                        'display': 'Systolic blood pressure'
                    }]
                },
                'valueQuantity': {
                    'value': bp.systolic,
                    'unit': 'mmHg',
                    'system': 'http://unitsofmeasure.org',
                    'code': 'mm[Hg]'
                }
            },
            {
                'code': {
                    'coding': [{
                        'system': 'http://loinc.org',
                        'code': '8462-4',
                        'display': 'Diastolic blood pressure'
                    }]
                },
                'valueQuantity': {
                    'value': bp.diastolic,
                    'unit': 'mmHg',
                    'system': 'http://unitsofmeasure.org',
                    'code': 'mm[Hg]'
                }
            }
        ]
    )
    return fhir_bp

def convert_body_temperature_to_fhir(bt):
    fhir_bt = Observation(
        id=str(bt.temperature_id),
        status='final',
        category=[{
            'coding': [{
                'system': 'http://terminology.hl7.org/CodeSystem/observation-category',
                'code': 'vital-signs',
                'display': 'Vital Signs'
            }]
        }],
        code={
            'coding': [{
                'system': 'http://loinc.org',
                'code': '8310-5',
                'display': 'Body temperature'
            }]
        },
        subject={'reference': f'Patient/{bt.patient_id}'},
        effectiveDateTime=bt.measurement_date.isoformat(),
        valueQuantity={
            'value': float(bt.temperature),
            'unit': 'degrees C',
            'system': 'http://unitsofmeasure.org',
            'code': 'Cel'
        }
    )
    return fhir_bt

def convert_pulse_oximetry_to_fhir(po):
    fhir_po = Observation(
        id=str(po.oximetry_id),
        status='final',
        category=[{
            'coding': [{
                'system': 'http://terminology.hl7.org/CodeSystem/observation-category',
                'code': 'vital-signs',
                'display': 'Vital Signs'
            }]
        }],
        code={
            'coding': [{
                'system': 'http://loinc.org',
                'code': '2708-6',
                'display': 'Oxygen saturation in Arterial blood'
            }]
        },
        subject={'reference': f'Patient/{po.patient_id}'},
        effectiveDateTime=po.measurement_date.isoformat(),
        valueQuantity={
            'value': float(po.spo2),
            'unit': '%',
            'system': 'http://unitsofmeasure.org',
            'code': '%'
        }
    )
    return fhir_po

def convert_respiration_to_fhir(resp):
    fhir_resp = Observation(
        id=str(resp.respiration_id),
        status='final',
        category=[{
            'coding': [{
                'system': 'http://terminology.hl7.org/CodeSystem/observation-category',
                'code': 'vital-signs',
                'display': 'Vital Signs'
            }]
        }],
        code={
            'coding': [{
                'system': 'http://loinc.org',
                'code': '9279-1',
                'display': 'Respiratory rate'
            }]
        },
        subject={'reference': f'Patient/{resp.patient_id}'},
        effectiveDateTime=resp.measurement_date.isoformat(),
        valueQuantity={
            'value': resp.rate,
            'unit': 'breaths/minute',
            'system': 'http://unitsofmeasure.org',
            'code': '/min'
        }
    )
    return fhir_resp

# Funkce pro získání všech záznamů pacienta ve formátu FHIR
def get_patient_records_fhir(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    pulses = Pulse.query.filter_by(patient_id=patient_id).all()
    blood_pressures = BloodPressure.query.filter_by(patient_id=patient_id).all()
    body_temperatures = BodyTemperature.query.filter_by(patient_id=patient_id).all()
    pulse_oximetries = PulseOximetry.query.filter_by(patient_id=patient_id).all()
    respirations = Respiration.query.filter_by(patient_id=patient_id).all()

    bundle_entries = [
        BundleEntry(resource=convert_patient_to_fhir(patient))
    ]

    for pulse in pulses:
        bundle_entries.append(BundleEntry(resource=convert_pulse_to_fhir(pulse)))
    for bp in blood_pressures:
        bundle_entries.append(BundleEntry(resource=convert_blood_pressure_to_fhir(bp)))
    for bt in body_temperatures:
        bundle_entries.append(BundleEntry(resource=convert_body_temperature_to_fhir(bt)))
    for po in pulse_oximetries:
        bundle_entries.append(BundleEntry(resource=convert_pulse_oximetry_to_fhir(po)))
    for resp in respirations:
        bundle_entries.append(BundleEntry(resource=convert_respiration_to_fhir(resp)))

    bundle = Bundle(
        type="collection",
        entry=bundle_entries
    )

    return bundle

# Route pro export záznamů pacienta ve formátu FHIR
@app.route('/export_fhir/<int:patient_id>', methods=['GET'])
def export_patient_records_fhir(patient_id):
    fhir_bundle = get_patient_records_fhir(patient_id)
    fhir_dict = fhir_bundle.dict()

    # Convert date and Decimal objects to serializable types
    def convert_dates_and_decimals(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, (date, datetime)):
                    obj[key] = value.isoformat()
                elif isinstance(value, Decimal):
                    obj[key] = float(value)
                elif isinstance(value, list):
                    obj[key] = [convert_dates_and_decimals(item) for item in value]
                elif isinstance(value, dict):
                    obj[key] = convert_dates_and_decimals(value)
        return obj

    fhir_dict = convert_dates_and_decimals(fhir_dict)

    file_path = f'patient_{patient_id}_records.json'
    with open(file_path, 'w') as f:
        json.dump(fhir_dict, f, indent=2)
    return jsonify({"message": f"Patient records exported to {file_path}"}), 200

# Route pro hlavní stránku
@app.route('/')
def home():
    return render_template('home.html')

# Route pro seznam pacientů
@app.route('/patients')
def patient_list():
    patients = Patient.query.all()
    return render_template('patients.html', patients=patients)

# Route pro přidání pacienta
@app.route('/add_patient', methods=['GET', 'POST'])
def add_patient():
    if request.method == 'POST':
        first_name = request.form.get('first_name', '')
        last_name = request.form.get('last_name', '')
        birth_date = request.form.get('birth_date', '')
        gender = request.form.get('gender', '')
        address = request.form.get('address', '')
        phone = request.form.get('phone', '')

        existing_patient = Patient.query.filter_by(first_name=first_name, last_name=last_name).first()
        if existing_patient is None:
            new_patient = Patient(
                first_name=first_name,
                last_name=last_name,
                birth_date=datetime.strptime(birth_date, '%Y-%m-%d').date() if birth_date else None,
                gender=gender,
                address=address,
                phone=phone
            )
            db.session.add(new_patient)
            db.session.commit()
            return redirect(url_for('patient_list'))
        else:
            return f"Patient {first_name} {last_name} already exists."
    return render_template('add_patient.html')

# Route pro smazání pacienta
@app.route('/delete_patient/<int:patient_id>', methods=['POST'])
def delete_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    db.session.delete(patient)
    db.session.commit()
    return redirect(url_for('patient_list'))

# Route pro seznam doktorů
@app.route('/doctors')
def doctor_list():
    doctors = Doctor.query.all()
    return render_template('doctors.html', doctors=doctors)

# Route pro přidání doktora
@app.route('/add_doctor', methods=['GET', 'POST'])
def add_doctor():
    if request.method == 'POST':
        first_name = request.form.get('first_name', '')
        last_name = request.form.get('last_name', '')
        specialty = request.form.get('specialty', '')
        phone = request.form.get('phone', '')
        email = request.form.get('email', '')

        existing_doctor = Doctor.query.filter_by(email=email).first()
        if existing_doctor is None:
            new_doctor = Doctor(
                first_name=first_name,
                last_name=last_name,
                specialty=specialty,
                phone=phone,
                email=email
            )
            db.session.add(new_doctor)
            db.session.commit()
            return redirect(url_for('doctor_list'))
        else:
            return f"Doctor {first_name} {last_name} already exists."
    return render_template('add_doctor.html')

# Route pro smazání doktora
@app.route('/delete_doctor/<int:doctor_id>', methods=['POST'])
def delete_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    db.session.delete(doctor)
    db.session.commit()
    return redirect(url_for('doctor_list'))

# Route pro přidání záznamu
@app.route('/add_record/<string:record_type>', methods=['GET', 'POST'])
def add_record(record_type):
    if request.method == 'POST':
        form_data = request.form.to_dict()
        
        # Parse specific fields
        form_data['patient_id'] = int(form_data['patient_id'])
        form_data['doctor_id'] = int(form_data['doctor_id'])
        form_data['measurement_date'] = datetime.strptime(form_data['measurement_date'], '%Y-%m-%dT%H:%M')

        # Convert 'presence' field to boolean if it exists in the form data
        if 'presence' in form_data:
            form_data['presence'] = form_data['presence'].lower() == 'true'
        
        # Dynamically create the new record based on the record_type
        if record_type == 'pulse':
            new_record = Pulse(**form_data)
        elif record_type == 'blood_pressure':
            new_record = BloodPressure(**form_data)
        elif record_type == 'body_temperature':
            new_record = BodyTemperature(**form_data)
        elif record_type == 'pulse_oximetry':
            new_record = PulseOximetry(**form_data)
        elif record_type == 'respiration':
            new_record = Respiration(**form_data)
        else:
            return f"Record type {record_type} is not recognized.", 400
        
        db.session.add(new_record)
        db.session.commit()
        return redirect(url_for('home'))
    
    patients = Patient.query.all()
    doctors = Doctor.query.all()
    
    # Convert patients to a list of dictionaries
    patients_data = [{"patient_id": patient.patient_id, "first_name": patient.first_name, "last_name": patient.last_name, "gender": patient.gender} for patient in patients]
    
    return render_template('add_record.html', record_type=record_type, patients=patients, doctors=doctors, patients_data=patients_data)

# Route pro zobrazení záznamů pacienta
@app.route('/patient_records/<int:patient_id>')
def patient_records(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    pulses = Pulse.query.filter_by(patient_id=patient_id).all()
    blood_pressures = BloodPressure.query.filter_by(patient_id=patient_id).all()
    body_temperatures = BodyTemperature.query.filter_by(patient_id=patient_id).all()
    pulse_oximetries = PulseOximetry.query.filter_by(patient_id=patient_id).all()
    respirations = Respiration.query.filter_by(patient_id=patient_id).all()
    
    return render_template('patient_records.html', patient=patient, pulses=pulses, blood_pressures=blood_pressures, body_temperatures=body_temperatures, pulse_oximetries=pulse_oximetries, respirations=respirations)

# Route pro smazání záznamu
@app.route('/delete_record/<string:record_type>/<int:record_id>', methods=['POST'])
def delete_record(record_type, record_id):
    if record_type == 'pulse':
        record = Pulse.query.get_or_404(record_id)
    elif record_type == 'blood_pressure':
        record = BloodPressure.query.get_or_404(record_id)
    elif record_type == 'body_temperature':
        record = BodyTemperature.query.get_or_404(record_id)
    elif record_type == 'pulse_oximetry':
        record = PulseOximetry.query.get_or_404(record_id)
    elif record_type == 'respiration':
        record = Respiration.query.get_or_404(record_id)
    else:
        return f"Record type {record_type} is not recognized.", 400
    
    db.session.delete(record)
    db.session.commit()
    return redirect(url_for('patient_records', patient_id=record.patient_id))

# Hlavní blok pro spuštění Flask aplikace
if __name__ == "__main__":
    app.run(debug=True, port=80, host='0.0.0.0')
