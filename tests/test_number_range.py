import sqlalchemy as sa
from sqlalchemy_utils import NumberRangeType, NumberRange
from tests import DatabaseTestCase


class TestNumberRangeType(DatabaseTestCase):
    def create_models(self):
        class Building(self.Base):
            __tablename__ = 'building'
            id = sa.Column(sa.Integer, primary_key=True)
            persons_at_night = sa.Column(NumberRangeType)

            def __repr__(self):
                return 'Building(%r)' % self.id

        self.Building = Building

    def test_save_number_range(self):
        building = self.Building(
            persons_at_night=NumberRange(1, 3)
        )

        self.session.add(building)
        self.session.commit()

        building = self.session.query(self.Building).first()
        assert building.persons_at_night.min_value == 1
        assert building.persons_at_night.max_value == 3


class TestNumberRange(object):
    def test_equality_operator(self):
        assert NumberRange(1, 3) == NumberRange(1, 3)

    def test_str_representation(self):
        assert str(NumberRange(1, 3)) == '[1, 3]'
