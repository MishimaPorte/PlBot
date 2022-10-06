from email.policy import default
from enum import unique
from pyexpat import model
from tortoise.models import Model
from tortoise.fields import (
    BigIntField,
    ForeignKeyField,
    ManyToManyField,
    OneToOneField,
    CharField,
    IntField,
    BooleanField,
    CASCADE,
)


class TgUser(Model):
    id = BigIntField(pk=True)
    last = IntField(default=0)
    last_amount = IntField(default=0)


class Shared(Model):
    shared_to = ForeignKeyField(model_name="models.TgUser")
    playlist = ForeignKeyField(model_name="models.Playlist")
    accepted = BooleanField(default=False)


class Audio(Model):
    file_unique_id = CharField(max_length=50, unique=True)
    name = CharField(max_length=20, default="name")
    file_id = CharField(max_length=100, default="file_id")


class Playlist(Model):
    name = CharField(max_length=40, unique=True)
    owner = ForeignKeyField(model_name="models.TgUser", related_name="playlists")
    audios = ManyToManyField(model_name="models.Audio", on_delete=CASCADE)
    active = BooleanField(default=False)

    class Meta:
        unique_together = (("name", "owner"),)
