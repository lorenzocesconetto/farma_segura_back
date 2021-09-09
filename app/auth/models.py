from datetime import datetime
from flask import current_app
from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager
from itsdangerous import JSONWebSignatureSerializer as UntimedSerializer, TimedJSONWebSignatureSerializer as TimedSerializer, BadSignature, SignatureExpired


class Permission:
    READ = 2 ** 0
    CREATE = 2 ** 1
    DELETE = 2 ** 2
    ADMIN = 2 ** 3  # Developers only


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    permissions = db.Column(db.Integer, nullable=False)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self) -> str:
        return f'<Role {self.name}>'

    def __str__(self) -> str:
        return self.name

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm

    @staticmethod
    def insert_roles():
        roles = {
            'Owner': [Permission.READ, Permission.DELETE],
            'Admin': [Permission.ADMIN],
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            db.session.add(role)
        db.session.commit()


class AnonymousUser(AnonymousUserMixin):
    def can(self, permission):
        return False

    @property
    def is_admin(self):
        return False


class User(UserMixin, db.Model):
    email_confirmation_key = 'email_confirmation'
    reset_password_key = 'reset_password'
    id = db.Column(db.Integer, primary_key=True)

    cpf = db.Column(db.BigInteger, nullable=False)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(128), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    last_seen = db.Column(
        db.DateTime(), default=datetime.utcnow, nullable=False)
    member_since = db.Column(
        db.DateTime(), default=datetime.utcnow, nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))

    profiles = db.relationship(
        "UserAccessProfile", back_populates="user", cascade="all,delete")

    # scheduled_user_medication = db.relationship('ScheduledUserMedication', backref='user', lazy='dynamic')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None and self.email in current_app.config['ADMINS']:
            self.role = Role.query.filter_by(name='Administrator').first()

    def __repr__(self):
        return f'<User {self.first_name}>'

    def __str__(self):
        return self.first_name

    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
        }

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def generate_auth_token(self, expiration):
        if expiration is None:
            s = UntimedSerializer(secret_key=current_app.config['SECRET_KEY'])
        else:
            s = TimedSerializer(
                secret_key=current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id}).decode('utf-8')

    @staticmethod
    def verify_auth_token(token):
        s = TimedSerializer(secret_key=current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        # except SignatureExpired:
        #     return None
        # except BadSignature:
        #     return None
        except:
            try:
                s = UntimedSerializer(
                    secret_key=current_app.config['SECRET_KEY'])
                data = s.loads(token)
            except:
                return None
        return User.query.get(data['id'])

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=3600):
        s = TimedSerializer(
            secret_key=current_app.config['SECRET_KEY'], expires_in=expires_in)
        return s.dumps({self.reset_password_key: self.id}).decode('utf-8')

    def get_email_confirmation_token(self):
        s = TimedSerializer(secret_key=current_app.config['SECRET_KEY'])
        return s.dumps({self.email_confirmation_key: self.id}).decode('utf-8')

    @classmethod
    def verify_reset_password_token(cls, token):
        s = TimedSerializer(secret_key=current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(id)

    @classmethod
    def verify_email_confirmation_token(cls, token):
        s = TimedSerializer(secret_key=current_app.config['SECRET_KEY'])
        try:
            id = s.loads(token)[cls.email_confirmation_key]
        except:
            return
        return User.query.get(id)

    def can(self, permission):
        return self.role is not None and self.role.has_permission(permission)

    @property
    def is_admin(self):
        return self.can(Permission.ADMIN)

    @property
    def is_deliveryman(self):
        return self.can(Permission.DELIVERY)


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


login_manager.anonymous_user = AnonymousUser
