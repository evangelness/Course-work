from dataclasses import dataclass, field
from enum import Enum
import uuid


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


# --- Каталог послуг ---
SERVICES_CATALOG = {
    1: {"name": "Первинна консультація терапевта", "specialization": Specialization.THERAPIST},
    2: {"name": "Перев'язка та огляд хірурга", "specialization": Specialization.SURGEON},
    3: {"name": "ЕКГ та консультація кардіолога", "specialization": Specialization.CARDIOLOGIST},
    4: {"name": "Лікування карієсу", "specialization": Specialization.DENTIST},
    5: {"name": "Професійна чистка зубів", "specialization": Specialization.DENTIST}
}


DECOR = "────୨ৎ────"
LINE = "─" * 45


# --- Основні класи ---
@dataclass
class Patient:
    """Клас, що описує пацієнта (структура даних)."""
    full_name: str
    age: int
    phone_number: str
    patient_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])


class MedicalService:
    """Клас для медичної послуги з інкапсуляцією, валідацією та статусами."""
    
    def __init__(self, patient: Patient, service_name: str, specialization: Specialization, price: float):
        self.service_name = service_name
        self.patient = patient
        self.specialization = specialization
        self.status = AppointmentStatus.SCHEDULED 
        
        self.price = price

    @property
    def price(self) -> float:
        return self._price

    @price.setter
    def price(self, value: float):
        if value < 0:
            raise ValueError("Ціна медичної послуги не може бути від'ємною!")
        self._price = value

    def change_status(self, new_status: AppointmentStatus):
        self.status = new_status


# --- Блок демонстрації ---
if __name__ == "__main__":
    print(f"\n{DECOR} Система реєстрації медичних послуг {DECOR}\n")
    
    
    print("📋 Каталог доступних послуг:")
    for key, data in SERVICES_CATALOG.items():
        print(f"  [{key}] {data['name']} (Напрямок: {data['specialization'].value})")
    print(f"\n{LINE}\n")
    
    try:
        
        print("👤 Дані пацієнта:")
        p_name = input("   Введіть ПІБ: ")
        p_age = int(input("   Введіть вік: "))
        
        print(f"\n{LINE}\n")
        
        
        print(" Оформлення послуги:")
        service_choice = int(input("   Оберіть номер послуги з каталогу (1-5): "))
        
        if service_choice not in SERVICES_CATALOG:
            raise ValueError("Обрано неіснуючий номер послуги! Будь ласка, оберіть від 1 до 5.")
            
        selected_service_data = SERVICES_CATALOG[service_choice]
        s_price = float(input("   Введіть вартість послуги (грн): "))

        current_patient = Patient(full_name=p_name, age=p_age, phone_number="+380990000000")
        
        current_service = MedicalService(
            patient=current_patient, 
            service_name=selected_service_data["name"],
            specialization=selected_service_data["specialization"], 
            price=s_price
        )

        # Вивід інформації про створений запис
        print(f"\n{DECOR} Чек послуги {DECOR}")
        print(f"✅ Послуга «{current_service.service_name}» успішно зареєстрована!")
        print(f"👤 Пацієнт: {current_service.patient.full_name} (ID: {current_service.patient.patient_id}) | Вік: {current_service.patient.age}")
        print(f"🏥 Напрямок: {current_service.specialization.value}")
        print(f"🔄 Статус: {current_service.status.value}")
        print(f"💰 До сплати: {current_service.price} грн")
        print(LINE)

        print("\n⚙️ Оновлення статусу...")
        current_service.change_status(AppointmentStatus.IN_PROGRESS)
        print(f"🔄 Новий статус: {current_service.status.value}")

    except ValueError as e:
        print(f" Помилка валідації: {e}")
    except Exception as e:
        print(f" Виникла непередбачувана помилка: {e}")
