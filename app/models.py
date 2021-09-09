from datetime import datetime
import croniter
from app import db
from sqlalchemy import Index, text, and_, UniqueConstraint
from sqlalchemy.sql import func, cast
from sqlalchemy.dialects import postgresql
import pandas as pd


def to_tsvector_ix(*columns):
    s = " || ' ' || ".join(columns)
    return func.to_tsvector('portuguese', text(s))


class UserAccessProfile(db.Model):
    # id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'user.id'), nullable=False, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey(
        'profile.id'), nullable=False, primary_key=True)
    is_owner = db.Column(db.Boolean, nullable=False)
    notifications_on = db.Column(db.Boolean, nullable=False, default=True)
    user = db.relationship('User', back_populates='profiles')
    profile = db.relationship(
        'Profile', back_populates='users')  # cascade="all,delete"
    # user = db.relationship('User', foreign_keys=[user_id], backref='sub_profiles_access')
    # sub_profile = db.relationship('SubProfile', foreign_keys=[sub_profile_id], backref='users_access')
    __table_args__ = (UniqueConstraint('user_id', 'profile_id'), )

    def to_dict(self):
        return {
            **self.profile.to_dict(),
            'is_owner': self.is_owner,
            'notifications_on': self.notifications_on,
        }

    @classmethod
    def check_has_access(cls, user, profile):
        return cls.get_access_instance(user=user, profile=profile) is not None

    @classmethod
    def check_is_owner(cls, user, profile):
        access_instance = cls.get_access_instance(
            user=user, profile=profile)
        if access_instance is None:
            return False
        return access_instance.is_owner

    @classmethod
    def get_access_instance(cls, user, profile):
        if profile is None or user is None:
            return None
        user_access_profile = UserAccessProfile.query.filter_by(
            user_id=user.id, profile_id=profile.id).first()
        if user_access_profile:
            return user_access_profile
        return None

    # @classmethod
    # def delete_profile(cls, user, profile):
    #     access_instance = cls.get_access_instance(user=user, profile=profile)

    # @staticmethod
    # def has_view_permission(user, sub_profile):
    #     if UserAccessSubProfile.query.filter_by(user_id=user.id, sub_profile_id=sub_profile.id).first():
    #         return True
    #     return False


class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    cpf = db.Column(db.BigInteger, nullable=False)
    username = db.Column(db.String(32), nullable=False, unique=True)
    inventories = db.relationship(
        'MedicationInventory', backref='profile', lazy='dynamic', cascade="all,delete")
    symptoms = db.relationship(
        'ProfileSymptom', backref='profile', lazy='dynamic', cascade="all,delete")
    medications_taken = db.relationship(
        'MedicationTaken', backref='profile', lazy='dynamic', cascade="all,delete")
    scheduled_medications = db.relationship(
        'ScheduledProfileMedication', backref='profile', lazy='dynamic', cascade="all,delete")
    users = db.relationship("UserAccessProfile",
                            back_populates="profile", cascade="all,delete")

    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'cpf': self.cpf,
            'username': self.username,
        }


class Medication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.BigInteger, nullable=False, unique=True)
    codigo_produto = db.Column(db.BigInteger, nullable=False)
    registro = db.Column(db.BigInteger, nullable=False)
    numero_registro = db.Column(db.BigInteger, nullable=False)
    numero_processo = db.Column(db.BigInteger, nullable=False)
    tipo_produto = db.Column(db.Integer, nullable=False)
    nome_comercial = db.Column(db.String(128), nullable=False)
    codigo_bula_paciente = db.Column(db.String(178))
    codigo_bula_profissional = db.Column(db.String(178))
    categoria_regulatoria = db.Column(db.String(32), nullable=False)
    atc = db.Column(db.String(128))  # classesTerapeuticas
    cnpj = db.Column(db.BigInteger)
    razao_social = db.Column(db.String(128))
    apresentacao = db.Column(db.String(200), nullable=False)
    formas_farmaceuticas = db.Column(db.String(128))
    principios_ativos = db.Column(db.String(1300))
    restricao_prescricao = db.Column(db.String(140))
    restricao_uso = db.Column(db.String(128))
    tarja = db.Column(db.String(32))
    apresentacao_fracionada = db.Column(db.Boolean)
    medicamento_referencia = db.Column(db.Boolean)
    scheduled_profile_medication = db.relationship(
        'ScheduledProfileMedication', backref='medication', lazy='dynamic')
    medication_taken = db.relationship(
        'MedicationTaken', backref='medication', lazy='dynamic')
    inventories = db.relationship(
        'MedicationInventory', backref='medication', lazy='dynamic')

    __ts_vector__ = to_tsvector_ix(
        'nome_comercial', 'apresentacao',)

    __table_args__ = (Index('ix_medication___ts_vector__',
                      __ts_vector__, postgresql_using='gin'),)

    def to_dict(self):
        return {
            'id': self.id,
            'nome_comercial': self.nome_comercial,
            'apresentacao': self.apresentacao,
            'razao_social': self.razao_social,
            'principios_ativos': self.principios_ativos
        }

    def insert_medications():
        df = pd.read_csv('anvisa_scraped.csv')
        for i, row in df.iterrows():
            if not Medication.query.filter_by(codigo=row['codigo']).first():
                db.session.add(Medication(
                    codigo=row['codigo'],
                    codigo_produto=row['codigo_produto'],
                    registro=row['registro'],
                    numero_registro=row['numero_registro'],
                    numero_processo=row['numero_processo'],
                    tipo_produto=row['tipo_produto'],
                    nome_comercial=row['nome_comercial'],
                    codigo_bula_paciente=row['codigo_bula_paciente'],
                    codigo_bula_profissional=row['codigo_bula_profissional'],
                    categoria_regulatoria=row['categoria_regulatoria'],
                    atc=row['atc'],
                    cnpj=row['cnpj'],
                    razao_social=row['razao_social'],
                    apresentacao=row['apresentacao'],
                    formas_farmaceuticas=row['formas_farmaceuticas'],
                    principios_ativos=row['principios_ativos'],
                    restricao_prescricao=row['restricao_prescricao'],
                    restricao_uso=row['restricao_uso'],
                    tarja=row['tarja'],
                    apresentacao_fracionada=row['apresentacao_fracionada'] == 'S',
                    medicamento_referencia=row['medicamento_referencia'] == 'S',
                ))
        db.session.commit()


class MedicationInventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey(
        'profile.id'), nullable=False)
    medication_id = db.Column(db.Integer, db.ForeignKey(
        'medication.id'), nullable=False)
    inventory = db.Column(db.Integer)
    __table_args__ = (UniqueConstraint('medication_id', 'profile_id'), )

    def to_dict(self):
        return {
            'profile_id': self.profile_id,
            'medication_id': self.medication_id,
            'inventory': self.inventory,
        }


class ScheduledProfileMedication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey(
        'profile.id'), nullable=False)
    medication_id = db.Column(db.Integer, db.ForeignKey(
        'medication.id'), nullable=False)
    cron_schedule = db.Column(db.String(32), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        data = self.cron_schedule.split()
        minute = int(data[0])
        hour = int(data[1])
        # splitted_cron = item.cron_schedule.split()
        # if splitted_cron[2] == '*':
        message = 'Todo dia'
        # elif splitted_cron[2] == '*/2':
        #     message = 'Dia sim, dia não'
        return {
            'id': self.id,
            'hour': hour,
            'minute': minute,
            'profile_id': self.profile_id,
            'medication': self.medication.to_dict(),
            'cron_schedule': self.cron_schedule,
            'quantity': self.quantity,
            'message': message,
        }

    def get_next_scheduled(self, date: datetime):
        cron = croniter.croniter(self.cron_schedule, date)
        next_date = cron.get_next(datetime)
        prev_date = cron.get_prev(datetime)
        if next_date.date() == date.date():
            return next_date
        elif prev_date.date() == date.date():
            return prev_date
        else:
            return None

    def filter_day(self, date: datetime):
        return bool(self.get_next_scheduled(date))


class MedicationTaken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey(
        'profile.id'), nullable=False)
    medication_id = db.Column(db.Integer, db.ForeignKey(
        'medication.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    updated_timestamp = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=False)
    original_timestamp = db.Column(db.DateTime, nullable=False)
    taken = db.Column(db.Boolean, nullable=False)

    @staticmethod
    def get_history(profile_id, min_date, max_date):
        return (MedicationTaken.query.filter_by(profile_id=profile_id)
                .filter(
                    and_(
                        MedicationTaken.original_timestamp >= min_date,
                        MedicationTaken.original_timestamp < max_date,
                    )
        ).all())

    def to_dict(self):
        return {
            'id': self.id,
            'profile_id': self.profile_id,
            'medication': self.medication.to_dict(),
            'quantity': self.quantity,
            'original_timestamp': self.original_timestamp,
            'taken': self.taken,
        }


class Pharmacist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    role = db.Column(db.String)
    whatsapp_number = db.Column(db.String, unique=True, nullable=False)
    profile_pic_url = db.Column(db.String)

    @classmethod
    def insert_pharmacists(cls):
        pharmacists = [
            {
                'name': 'Lorenzo Cesconetto',
                'role': 'Farmacêutico',
                'whatsapp_number': '5519982652693',
                'profile_pic_url': r'https://firebasestorage.googleapis.com/v0/b/farma-segura.appspot.com/o/pharmacist_profile_picture%2Fpharmacist_profile.jpg?alt=media'
            },
            {
                'name': 'Vicenzo Cano',
                'role': 'Farmacêutico',
                'whatsapp_number': '552733400751',
                'profile_pic_url': r'https://firebasestorage.googleapis.com/v0/b/farma-segura.appspot.com/o/pharmacist_profile_picture%2Fpharmacist_profile.jpg?alt=media'
            },
        ]
        for p in pharmacists:
            pharmacist = cls.query.filter_by(
                whatsapp_number=p['whatsapp_number']).first()
            if pharmacist is None:
                pharmacist = cls(whatsapp_number=p['whatsapp_number'])
            pharmacist.name = p['name']
            pharmacist.role = p['role']
            pharmacist.profile_pic_url = p['profile_pic_url']
            db.session.add(pharmacist)
        db.session.commit()


class ProfileSymptom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey(
        'profile.id'), nullable=False)
    sympton_id = db.Column(db.Integer, db.ForeignKey(
        'symptom.id'), nullable=False)
    intensity = db.Column(db.Integer, nullable=False)
    submited_datetime = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=False)
    marked_datetime = db.Column(db.DateTime, nullable=False)
    __table_args__ = (UniqueConstraint(
        'sympton_id', 'profile_id', 'marked_datetime'), )


class Symptom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    profiles_symptom = db.relationship(
        'ProfileSymptom', backref='symptom', lazy='dynamic')

    @classmethod
    def insert_symptoms(cls):
        symptoms = [
            'Afta',
            'Cansaço',
            'Coceira',
            'Confusão',
            'Convulsão',
            'Diarréia',
            'Dificuldade para engolir',
            'Dor no corpo',
            'Enjôo',
            'Falta de ar',
            'Febre',
            'Formigamento',
            'Inchaço',
            'Insônia',
            'Perda de apetite',
            'Prisão de ventre',
            'Problema com cateter',
            'Reação na pele',
            'Sangramento',
            'Sangue na urina',
            'Vômito',
            'Tontura',
        ]
        for name in symptoms:
            symptom = cls.query.filter_by(name=name).first()
            if symptom is None:
                symptom = cls(name=name)
                db.session.add(symptom)
        db.session.commit()
