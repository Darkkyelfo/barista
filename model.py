from os import path

import peewee

from util import get_major_version

db = peewee.SqliteDatabase(f'{path.dirname(path.realpath(__file__))}/barista.db')


class BaseModel(peewee.Model):
    """Classe model base"""

    class Meta:
        # Indica em qual banco de dados a tabela
        # 'author' sera criada (obrigatorio). Neste caso,
        # utilizamos o banco 'codigo_avulso.db' criado anteriormente
        database = db


class Java(BaseModel):
    """
    Classe que representa a tabela Java
    """
    id = peewee.AutoField()
    version = peewee.CharField()
    major_version = peewee.IntegerField()
    link = peewee.CharField()
    repository = peewee.CharField()
    so = peewee.CharField()

    @staticmethod
    def save_multiple_versions(version_dict, so, repository):
        versions_as_list = [{"version": version, "link": link, "so": so, "repository": repository,
                             "major_version": get_major_version(version)} for (version, link)
                            in version_dict.items()]
        Java.insert_many(versions_as_list).execute()


class Maven(BaseModel):
    """
    Classe que representa a tabela Java
    """
    id = peewee.AutoField()
    version = peewee.CharField()
    link = peewee.CharField()

    @staticmethod
    def save_multiple_versions(version_dict):
        versions_as_list = [{"version": version, "link": link} for (version, link) in version_dict.items()]
        Maven.insert_many(versions_as_list).execute()

    @staticmethod
    def reset_dataset(versions_dict):
        Maven.delete().execute()
        Maven.save_multiple_versions(versions_dict)


class Environment(BaseModel):
    """
    Classe que representa a tabela de Environment
    """
    id = peewee.AutoField()
    id_maven = peewee.ForeignKeyField(Maven, to_field="id")
    id_java = peewee.ForeignKeyField(Java, to_field="id")
    name = peewee.CharField(unique=True)
    m2_repository = peewee.CharField()
