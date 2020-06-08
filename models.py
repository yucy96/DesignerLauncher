from exts import db
from sqlalchemy.orm import relationship
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import datetime


class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.String(200), primary_key=True)
    email = db.Column(db.String(80), primary_key=False, nullable=False, unique=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    birthday = db.Column(db.Date, nullable=True)
    gender = db.Column(db.Integer, nullable=True)
    position = db.Column(db.String(100), nullable=True)
    company_name = db.Column(db.String(80), nullable=True)
    identification = db.Column(db.Integer, nullable=True)
    description = db.Column(db.Text, nullable=True)

    def __init__(self, email, first_name, last_name, birthday=None, gender=None, position=None, company_name=None, identification=None, description=None):
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.birthday = birthday
        self.gender = gender
        self.position = position
        self.company_name = company_name
        self.identification = identification
        self.description = description

    def set_password(self, password):
        """Create hashed password."""
        self.password = generate_password_hash(password, method='sha256')

    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password, password)

    def generate_id(self):
        if self.first_name and self.last_name:
            self.id = self.first_name.lower() + '-' + self.last_name.lower() + '-' + str(uuid.uuid4().fields[-1])[:10]
            return 0
        else:
            return -1

    def __repr__(self):
        return f'Id: {self.id}. {self.first_name} {self.last_name}'


class Sale(db.Model):
    __tablename__ = 'sale'

    id = db.Column(db.String(130), primary_key=True)
    phase2_expected_sale = db.Column(db.Integer, nullable=True)
    phase3_expected_sale = db.Column(db.Integer, nullable=True)
    expected_price = db.Column(db.Integer, nullable=True)
    final_price = db.Column(db.Integer, nullable=True)

    def __init__(self, id, phase2_expected_sale=None, expected_price=None, phase3_expected_sale=None, final_price=None):
        self.id = id
        self.phase2_expected_sale = phase2_expected_sale
        self.phase3_expected_sale = phase3_expected_sale
        self.expected_price = expected_price
        self.final_price = final_price


class Work(db.Model):
    __tablename__ = 'work'

    id = db.Column(db.String(130), primary_key=True)
    phase = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(80), db.ForeignKey('user.id'))
    sale_id = db.Column(db.String(130), db.ForeignKey('sale.id'), nullable=True)
    name = db.Column(db.String(200), nullable=False)
    short_description = db.Column(db.Text, nullable=False)
    for_sale = db.Column(db.Boolean, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    category = db.Column(db.String(30), nullable=False)
    colors = db.Column(db.ARRAY(db.String(80)), nullable=False)
    sketch_pic = db.Column(db.ARRAY(db.Text), nullable=False)
    flat_pic = db.Column(db.ARRAY(db.Text), nullable=False)
    inspiration = db.Column(db.Text, nullable=False)
    details = db.Column(db.Text, nullable=False)
    design_type = db.Column(db.String(100), nullable=True)
    cover_image = db.Column(db.Text, nullable=False)
    tags = db.Column(db.ARRAY(db.String(50)))
    sales = relationship(Sale)

    # Phase 2 required columns
    # material_id = db.Column(db.Integer, db.ForeignKey('material.id'), nullable=True)
    materials = relationship("Material", backref="work")
    model_fit = db.Column(db.ARRAY(db.Text), nullable=True)

    # Phase 3 required columns
    # size_id = db.Column(db.Integer, db.ForeignKey('size.id'), nullable=True)
    sizes = relationship("Size", backref="work")
    model_pics = db.Column(db.ARRAY(db.Text))
    detail_pics = db.Column(db.ARRAY(db.Text))
    time = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow)

    def __init__(self, id, phase=None, user_id=None, sale_id=None, name=None, short_description=None, for_sale=None,
                 gender=None, category=None, colors=None, sketch_pic=None, flat_pic=None, inspiration=None,
                 details=None, design_type=None, cover_image=None, tags=None, model_fit=None, model_pics=None,
                 detail_pics=None):
        self.id = id
        self.phase = phase
        self.user_id = user_id
        self.sale_id = sale_id
        self.name = name
        self.short_description = short_description
        self.for_sale = for_sale
        self.gender = gender
        self.category = category
        self.colors = colors
        self.sketch_pic = sketch_pic
        self.flat_pic = flat_pic
        self.inspiration = inspiration
        self.details = details
        self.design_type = design_type
        self.cover_image = cover_image
        self.tags = tags
        self.model_fit = model_fit
        self.model_pics = model_pics
        self.detail_pics = detail_pics


class Material(db.Model):
    __tablename__ = 'material'

    id = db.Column(db.String(130), primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    pic = db.Column(db.Text, nullable=True)
    part = db.Column(db.String(200), nullable=False)
    color = db.Column(db.String(50), nullable=True)
    work_id = db.Column(db.String(130), nullable=False)
    phase = db.Column(db.Integer, nullable=False)
    # db.ForeignKeyConstraint(['work_id', 'phase'], ['work.id', 'work.phase'])
    __table_args__ = (db.ForeignKeyConstraint([work_id, phase],
                                           [Work.id, Work.phase]),
                      {})

    def __init__(self, id, name=None, pic=None, part=None, color=None, work_id=None, phase=None):
        self.id = id
        self.name = name
        self.pic = pic
        self.part = part
        self.color = color
        self.work_id = work_id
        self.phase = phase

class Size(db.Model):
    __tablename__ = 'size'

    id = db.Column(db.String(130), primary_key=True)
    size = db.Column(db.String(50), nullable=False)
    shoulder = db.Column(db.Integer, nullable=True)
    bust = db.Column(db.Integer, nullable=True)
    waist = db.Column(db.Integer, nullable=True)
    hip = db.Column(db.Integer, nullable=True)
    length = db.Column(db.Integer, nullable=True)
    width = db.Column(db.Integer, nullable=True)
    height = db.Column(db.Integer, nullable=True)
    work_id = db.Column(db.String(130), nullable=False)
    phase = db.Column(db.Integer, nullable=False)
    # db.ForeignKeyConstraint(['work_id', 'phase'], ['work.id', 'work.phase'])
    __table_args__ = (db.ForeignKeyConstraint([work_id, phase],
                                              [Work.id, Work.phase]),
                      {})

    def __init__(self, id, size=None, shoulder=None, bust=None, waist=None, hip=None, length=None, width=None, height=None, work_id=None, phase=None):
        self.id = id
        self.size = size
        self.shoulder = shoulder
        self.bust = bust
        self.waist = waist
        self.hip = hip
        self.length = length
        self.width = width
        self.height = height
        self.work_id = work_id
        self.phase = phase


# class User(db.Model):
#     __tablename__ = 'user'
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     telephone = db.Column(db.String(11),nullable=False)
#     username = db.Column(db.String(50),nullable=False)
#     password = db.Column(db.String(100),nullable=False)
#
# class Question(db.Model):
#     __tablename__='question'
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     title = db.Column(db.String(100),nullable=False)
#     content = db.Column(db.Text,nullable=False)
#     # now()获取的是服务器第一次运行的时间
#     # now 就是每次创建一个模型的时候，都获取当前的时间
#     create_time = db.Column(db.DateTime,default=datetime.now)
#     author_id = db.Column(db.Integer,db.ForeignKey('user.id'))
#     author = db.relationship('User',backref=db.backref('question'))
#
# class Answer(db.Model):
#     __tablename__ = 'answer'
#     id = db.Column(db.Integer,primary_key=True,autoincrement=True)
#     content = db.Column(db.Text,nullable=False)
#     question_id = db.Column(db.Integer,db.ForeignKey('question.id'))
#     author_id = db.Column(db.Integer,db.ForeignKey('user.id'))
#     create_time = db.Column(db.DateTime, default=datetime.now)
#
#     question = db.relationship('Question',backref=db.backref('answers', order_by=create_time.desc()))
#     author = db.relationship('User',backref=db.backref('answers'))