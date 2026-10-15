from dataclasses import dataclass, field
from enum import Enum
import uuid


# --- 1. ENUM ---
class Specialization(Enum):
    """Перелік медичних спеціалізацій."""
    THERAPIST = "Терапевт"
    SURGEON = "Хірург"
    CARDIOLOGIST = "Кардіолог"
    DENTIST = "Стоматолог"


class AppointmentStatus(Enum):
    """Перелік статусів медичного прийому."""
    SCHEDULED = "Заплановано"
    IN_PROGRESS = "В процесі"
    COMPLETED = "Завершено"
    CANCELLED = "Скасовано"


# Розширений каталог для демонстрації вибору
SERVICES_CATALOG = {
    1: {"name": "Первинна консультація", "type": "consultation", "specialization": Specialization.THERAPIST},
    2: {"name": "Повторна консультація", "type": "consultation", "specialization": Specialization.THERAPIST},
    3: {"name": "УЗД / ЕКГ", "type": "diagnostic", "specialization": Specialization.CARDIOLOGIST},
    4: {"name": "Хірургічне втручання (мале)", "type": "procedure", "specialization": Specialization.SURGEON},
    5: {"name": "Перев'язка", "type": "procedure", "specialization": Specialization.SURGEON},
    6: {"name": "Лікування карієсу", "type": "procedure", "specialization": Specialization.DENTIST},
}


# --- 2. БАЗОВІ СУТНОСТІ ТА НАСЛІДУВАННЯ ---
@dataclass
class Person:
    full_name: str
    phone_number: str


@dataclass
class Patient(Person):
    age: int
    patient_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])


@dataclass
class Doctor(Person):
    specialization: Specialization
    doctor_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])


# --- 3. ІЄРАРХІЯ ПОСЛУГ ТА ПОЛІМОРФІЗМ ---
class MedicalService:
    def __init__(self, service_name: str, base_price: float):
        self.service_name = service_name
        self.base_price = base_price

    @property
    def base_price(self) -> float:
        return self._base_price

    @base_price.setter
    def base_price(self, value: float):
        if value < 0:
            raise ValueError("Базова ціна не може бути від'ємною!")
        self._base_price = value

    def calculate_cost(self) -> float:
        return self.base_price


class Consultation(MedicalService):
    def __init__(self, service_name: str, base_price: float, doctor: Doctor):
        super().__init__(service_name, base_price)
        self.doctor = doctor

    def calculate_cost(self) -> float:
        return self.base_price


class DiagnosticService(MedicalService):
    def __init__(self, service_name: str, base_price: float, equipment_fee: float):
        super().__init__(service_name, base_price)
        self.equipment_fee = equipment_fee

    def calculate_cost(self) -> float:
        return self.base_price + self.equipment_fee


class Procedure(MedicalService):
    def __init__(self, service_name: str, base_price: float, complexity_multiplier: float):
        super().__init__(service_name, base_price)
        self.complexity_multiplier = complexity_multiplier

    def calculate_cost(self) -> float:
        return self.base_price * self.complexity_multiplier


# --- 4. КОМПОЗИЦІЯ ---
class Appointment:
    def __init__(self, patient: Patient, service: MedicalService, doctor: Doctor = None):
        self.patient = patient
        self.service = service
        self.doctor = doctor or getattr(service, 'doctor', None)
        self.status = AppointmentStatus.SCHEDULED


class ClinicManager:
    def __init__(self):
        self._appointments: list[Appointment] = []

    def add_appointment(self, appointment: Appointment):
        self._appointments.append(appointment)
        print(f"\n[МЕНЕДЖЕР] Запис для пацієнта '{appointment.patient.full_name}' додано до системи.")

    def show_all_appointments(self):
        print("\n=== РЕЄСТР ПРИЙОМІВ КЛІНІКИ ===")
        if not self._appointments:
            print("Реєстр порожній.")
            return
            
        for idx, appt in enumerate(self._appointments, start=1):
            final_price = appt.service.calculate_cost()
            doc_info = appt.doctor.full_name if appt.doctor else "Без прив'язки"
            
            print(f"{idx}. Пацієнт: {appt.patient.full_name} | Послуга: {appt.service.service_name} "
                  f"| Лікар: {doc_info} ({appt.doctor.specialization.value if appt.doctor else ''}) "
                  f"| До сплати: {final_price:.2f} грн | Статус: {appt.status.value}")
        print("===============================\n")


# --- ДЕМОНСТРАЦІЯ ---
if __name__ == "__main__":
    print("--- Система реєстратури медичного закладу ---")
    manager = ClinicManager()
    
    try:
        # 1. Ввід даних пацієнта
        print("\n👤 Дані пацієнта:")
        p_name = input("Введіть ПІБ: ")
        p_phone = input("Введіть номер телефону: ")
        p_age = int(input("Введіть вік: "))
        
        current_patient = Patient(full_name=p_name, phone_number=p_phone, age=p_age)
        
        # 2. Вибір спеціалізації з Enum
        print("\n🏥 Доступні напрямки:")
        specializations = list(Specialization)
        for idx, spec in enumerate(specializations, start=1):
            print(f"[{idx}] {spec.value}")
            
        spec_choice = int(input("\nОберіть номер напрямку, до якого хочете звернутися: "))
        if not (1 <= spec_choice <= len(specializations)):
            raise ValueError("Обрано неіснуючий напрямок!")
            
        selected_specialization = specializations[spec_choice - 1]
        
        # Створюємо лікаря обраної спеціалізації для цього прийому
        duty_doctor = Doctor(
            full_name="Черговий Лікар", 
            phone_number="+380000000000", 
            specialization=selected_specialization
        )
        
        # 3. Вибір послуги (фільтрація каталогу за обраною спеціалізацією)
        print(f"\n📋 Каталог послуг для напрямку «{selected_specialization.value}»:")
        available_services = {k: v for k, v in SERVICES_CATALOG.items() if v["specialization"] == selected_specialization}
        
        if not available_services:
            print("На жаль, послуг для цього напрямку наразі немає.")
        else:
            for key, data in available_services.items():
                print(f"[{key}] {data['name']} (Тип: {data['type']})")
                
            service_choice = int(input("\nОберіть номер послуги: "))
            
            if service_choice not in available_services:
                raise ValueError("Обрано неіснуючий номер послуги!")
                
            selected = available_services[service_choice]
            base_price = float(input("Введіть базову вартість послуги (грн): "))
            
            # 4. Динамічне створення послуги (поліморфізм)
            current_service = None
            
            if selected["type"] == "consultation":
                current_service = Consultation(selected["name"], base_price, duty_doctor)
                
            elif selected["type"] == "diagnostic":
                eq_fee = float(input("Введіть амортизаційний збір за обладнання (грн): "))
                current_service = DiagnosticService(selected["name"], base_price, eq_fee)
                
            elif selected["type"] == "procedure":
                multiplier = float(input("Введіть коефіцієнт складності від 1 до 5: "))
                current_service = Procedure(selected["name"], base_price, multiplier)
                
            # 5. Оформлення прийому
            appointment = Appointment(patient=current_patient, service=current_service, doctor=duty_doctor)
            manager.add_appointment(appointment)

            # Вивід реєстру
            manager.show_all_appointments()

    except ValueError as e:
        print(f"\n[ПОМИЛКА ВАЛІДАЦІЇ] {e}")
    except Exception as e:
        print(f"\n[ПОМИЛКА] Виникла непередбачувана ситуація: {e}")