from sqlalchemy import Column, String, Integer, DateTime, Float
from datetime import datetime
from typing import Union
from  model import Base

import random
import string


class Produto(Base):
    __tablename__ = 'produto'

    id = Column(Integer, primary_key = True)
    codigo = Column(String(10), unique = True)
    nome = Column(String(140), unique = True)
    tipo = Column(String(100))
    valor = Column(Float)
    descricao = Column(String(255))
    cep = Column(String(9))
    logradouro = Column(String(255))
    numero = Column(Integer)
    complemento = Column(String(255))
    bairro = Column(String(255))
    localidade = Column(String(255))
    uf = Column(String(2))
    data_insercao = Column(DateTime, default=datetime.now())


    def __init__(self, nome:str, tipo:str, valor:float, descricao:str, 
                cep:str, logradouro:str, numero:int, complemento:str, 
                bairro:str, localidade:str, uf:str,
                data_insercao:Union[DateTime, None] = None):
        
        self.nome = nome
        self.tipo = tipo
        self.valor = valor
        self.descricao = descricao
        self.cep = cep
        self.logradouro = logradouro
        self.numero = numero
        self.complemento = complemento
        self.bairro = bairro
        self.localidade = localidade
        self.uf = uf
        self.codigo = self.gera_codigo()

        if data_insercao:
            self.data_insercao = data_insercao

    
    def gera_codigo(self):

        """ Gerador de código alfa numéricos de 10 caracteres automáticamente
        """
        
        _codigo = ''
        
        #Numeros randomicos
        _numeros = ''.join(str(random.randint(0,9)) for _ in range(5))
            
        #Letras randomicas 
        _codigo = ''.join(random.choice(string.ascii_uppercase) for _ in range(5))
        
        #retorna codigo
        return _codigo + _numeros