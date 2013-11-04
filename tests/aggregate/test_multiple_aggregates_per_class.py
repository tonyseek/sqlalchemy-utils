import sqlalchemy as sa
from sqlalchemy_utils.aggregates import aggregated_attr
from tests import TestCase


class TestAggregateValueGenerationForSimpleModelPaths(TestCase):
    def create_models(self):
        class Thread(self.Base):
            __tablename__ = 'thread'
            id = sa.Column(sa.Integer, primary_key=True)
            name = sa.Column(sa.Unicode(255))

            @aggregated_attr('comments')
            def comment_count(self):
                return sa.Column(sa.Integer, default=0)

            @aggregated_attr('comments', sa.func.max)
            def last_comment_id(self):
                return sa.Column(sa.Integer)

            comments = sa.orm.relationship(
                'Comment',
                backref='thread'
            )

        Thread.last_comment = sa.orm.relationship(
            'Comment',
            primaryjoin='Thread.last_comment_id == Comment.id',
            foreign_keys=[Thread.last_comment_id],
            viewonly=True
        )

        class Comment(self.Base):
            __tablename__ = 'comment'
            id = sa.Column(sa.Integer, primary_key=True)
            content = sa.Column(sa.Unicode(255))
            thread_id = sa.Column(sa.Integer, sa.ForeignKey('thread.id'))

        self.Thread = Thread
        self.Comment = Comment

    def test_assigns_aggregates_on_insert(self):
        thread = self.Thread()
        thread.name = u'some article name'
        self.session.add(thread)
        comment = self.Comment(content=u'Some content', thread=thread)
        self.session.add(comment)
        self.session.commit()
        self.session.refresh(thread)
        assert thread.comment_count == 1
        assert thread.last_comment_id == comment.id

    def test_assigns_aggregates_on_separate_insert(self):
        thread = self.Thread()
        thread.name = u'some article name'
        self.session.add(thread)
        self.session.commit()
        comment = self.Comment(content=u'Some content', thread=thread)
        self.session.add(comment)
        self.session.commit()
        self.session.refresh(thread)
        assert thread.comment_count == 1
        assert thread.last_comment_id == 1

    def test_assigns_aggregates_on_delete(self):
        thread = self.Thread()
        thread.name = u'some article name'
        self.session.add(thread)
        self.session.commit()
        comment = self.Comment(content=u'Some content', thread=thread)
        self.session.add(comment)
        self.session.commit()
        self.session.delete(comment)
        self.session.commit()
        self.session.refresh(thread)
        assert thread.comment_count == 0
        assert thread.last_comment_id is None