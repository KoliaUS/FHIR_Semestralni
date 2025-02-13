import datetime
from app import app, db, Patient, Doctor, Pulse, BloodPressure, BodyTemperature, PulseOximetry, Respiration

def setup_database(app):
    with app.app_context():
        db.create_all()

        # Add patients
        patients = [
            {"first_name": "Jan", "last_name": "Novák", "birth_date": datetime.datetime(1985, 1, 1), "gender": "Male", "address": "Praha 1, 11000", "phone": "123456789"},
            {"first_name": "Eva", "last_name": "Dvořáková", "birth_date": datetime.datetime(1992, 4, 20), "gender": "Female", "address": "Brno, 60200", "phone": "987654321"},
            {"first_name": "Tomáš", "last_name": "Marek", "birth_date": datetime.datetime(1975, 9, 15), "gender": "Male", "address": "Ostrava, 71000", "phone": "567890123"},
            {"first_name": "Michaela", "last_name": "Horáková", "birth_date": datetime.datetime(1990, 3, 10), "gender": "Female", "address": "Olomouc, 77900", "phone": "234567890"}
        ]

        for patient_data in patients:
            patient = Patient(**patient_data)
            db.session.add(patient)
        db.session.commit()

        # Add doctors
        doctors = [
            {"first_name": "Martin", "last_name": "Nový", "specialty": "Cardiology", "phone": "123123123", "email": "martin.novy@example.com"},
            {"first_name": "Anna", "last_name": "Procházková", "specialty": "General Practice", "phone": "321321321", "email": "anna.prochazkova@example.com"},
            {"first_name": "Petr", "last_name": "Svoboda", "specialty": "Pulmonology", "phone": "456456456", "email": "petr.svoboda@example.com"}
        ]

        for doctor_data in doctors:
            doctor = Doctor(**doctor_data)
            db.session.add(doctor)
        db.session.commit()

        # Add pulse measurements
        pulse_measurements = [
            {"patient_id": 1, "doctor_id": 1, "measurement_date": datetime.datetime.now(), "presence": True, "rate": 75, "regularity": "Regular", "irregular_type": None, "character": "Normal", "clinical_description": "Normal pulse"},
            {"patient_id": 2, "doctor_id": 2, "measurement_date": datetime.datetime.now(), "presence": True, "rate": 80, "regularity": "Irregular", "irregular_type": "Irregularly Irregular", "character": "Thready", "clinical_description": "Irregular pulse"}
        ]

        for measurement in pulse_measurements:
            pulse = Pulse(**measurement)
            db.session.add(pulse)
        db.session.commit()

        # Add blood pressure measurements
        bp_measurements = [
            {"patient_id": 1, "doctor_id": 1, "measurement_date": datetime.datetime.now(), "systolic": 120, "diastolic": 80, "mean_arterial_pressure": 93, "pulse_pressure": 40, "clinical_interpretation": "Normal blood pressure"},
            {"patient_id": 2, "doctor_id": 2, "measurement_date": datetime.datetime.now(), "systolic": 140, "diastolic": 90, "mean_arterial_pressure": 107, "pulse_pressure": 50, "clinical_interpretation": "Hypertension"}
        ]

        for measurement in bp_measurements:
            bp = BloodPressure(**measurement)
            db.session.add(bp)
        db.session.commit()

        # Add body temperature measurements
        temperature_measurements = [
            {"patient_id": 3, "doctor_id": 3, "measurement_date": datetime.datetime.now(), "temperature": 36.6, "body_exposure": "Appropriate clothing/bedding", "thermal_stress": None, "menstrual_cycle_day": None, "confounding_factors": None, "environmental_conditions": "Room temperature"},
            {"patient_id": 4, "doctor_id": 1, "measurement_date": datetime.datetime.now(), "temperature": 38.2, "body_exposure": "Reduced clothing/bedding", "thermal_stress": "Fever", "menstrual_cycle_day": 15, "confounding_factors": "Infection", "environmental_conditions": "Room temperature"}
        ]

        for measurement in temperature_measurements:
            temperature = BodyTemperature(**measurement)
            db.session.add(temperature)
        db.session.commit()

        # Add pulse oximetry measurements
        oximetry_measurements = [
            {"patient_id": 1, "doctor_id": 2, "measurement_date": datetime.datetime.now(), "spo2": 98.5, "spoc": 20.0, "spco": 0.5, "spmet": 0.2, "waveform": None, "interpretation": "Normal oxygen saturation"},
            {"patient_id": 2, "doctor_id": 3, "measurement_date": datetime.datetime.now(), "spo2": 95.0, "spoc": 19.5, "spco": 1.0, "spmet": 0.3, "waveform": None, "interpretation": "Mild hypoxia"}
        ]

        for measurement in oximetry_measurements:
            oximetry = PulseOximetry(**measurement)
            db.session.add(oximetry)
        db.session.commit()

        # Add respiration measurements
        respiration_measurements = [
            {"patient_id": 3, "doctor_id": 1, "measurement_date": datetime.datetime.now(), "presence": True, "rate": 16, "regularity": "Regular", "depth": "Normal", "clinical_description": "Normal respiration", "clinical_interpretation": "No issues"},
            {"patient_id": 4, "doctor_id": 2, "measurement_date": datetime.datetime.now(), "presence": True, "rate": 20, "regularity": "Irregular", "depth": "Shallow", "clinical_description": "Rapid and shallow breathing", "clinical_interpretation": "Possible respiratory distress"}
        ]

        for measurement in respiration_measurements:
            respiration = Respiration(**measurement)
            db.session.add(respiration)
        db.session.commit()

if __name__ == "__main__":
    setup_database(app)
