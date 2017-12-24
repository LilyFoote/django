"""
Many-to-many relationships

To define a many-to-many relationship, use ``ManyToManyField()``.

In this example, an ``Article`` can be published in multiple ``Publication``
objects, and a ``Publication`` has multiple ``Article`` objects.
"""
from django.db import models


class Publication(models.Model):
    title = models.CharField(max_length=30)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ('title',)


class Tag(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Article(models.Model):
    headline = models.CharField(max_length=100)
    # Assign a string as name to make sure the intermediary model is
    # correctly created. Refs #20207
    publications = models.ManyToManyField(Publication, name='publications')
    tags = models.ManyToManyField(Tag, related_name='tags')

    def __str__(self):
        return self.headline

    class Meta:
        ordering = ('headline',)


# Models to test correct related_name inheritance
class AbstractArticle(models.Model):
    class Meta:
        abstract = True

    publications = models.ManyToManyField(Publication, name='publications', related_name='+')


class InheritedArticleA(AbstractArticle):
    pass


class InheritedArticleB(AbstractArticle):
    pass


class AuthorManagerMixin:
    def favourited(self):
        return self.filter(follow__favourite=True)

    def add(self, *objs, favourite=False):
        follows = []
        for obj in objs:
            follows.append(Follow(author=self.instance, reader=obj, favourite=favourite))
        Follow.objects.bulk_create(follows)


class ReaderManagerMixin:
    def favourites(self):
        return self.filter(follow__favourite=True)

    def add(self, *objs, favourite=False):
        follows = []
        for obj in objs:
            follows.append(Follow(author=obj, reader=self.instance, favourite=favourite))
        Follow.objects.bulk_create(follows)


class Reader(models.Model):
    name = models.CharField(max_length=100)


class Author(models.Model):
    name = models.CharField(max_length=100)
    followers = models.ManyToManyField(
        Reader,
        through='Follow',
        related_name='following',
        manager_mixin=AuthorManagerMixin,
        related_manager_mixin=ReaderManagerMixin,
    )


class Follow(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    reader = models.ForeignKey(Reader, on_delete=models.CASCADE)
    favourite = models.BooleanField(default=False)
