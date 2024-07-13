from flask_openapi3 import OpenAPI, Info, Tag
from flask import redirect
from urllib.parse import unquote

from sqlalchemy.exc import IntegrityError

from model import Session, Produto
from logger import logger
from schemas import *
from flask_cors import CORS

info = Info(title="API de Serviços", version="1.0.0")
app = OpenAPI(__name__, info=info)
CORS(app)


home_tag = Tag(name="Documentação", description="Seleção de documentação: Swagger, Redoc ou RapiDoc")
produto_tag = Tag(name="Produto", description="Adição, visualização e remoção de produtos à base")
endereco_tag = Tag(name="Endereço", description="Visualização de endereço de api externa")


@app.get('/', tags=[home_tag])
def home():
    
    return redirect('/openapi')


@app.post('/add_produto', tags=[produto_tag],
          responses={"200": ProdutoViewSchema, "409": ErrorSchema, "400": ErrorSchema})
def add_produto(form: ProdutoSchema):
    """Adiciona um novo Produto à base de dados

    Retorna uma representação dos produtos cadastrados.
    """
    produto = Produto(
        nome=form.nome,
        tipo=form.tipo,
        valor=form.valor,
        descricao=form.descricao,
        cep=form.cep,
        logradouro=form.logradouro,
        numero=form.numero,
        complemento=form.complemento,
        bairro=form.bairro,
        localidade=form.localidade,
        uf=form.uf)
    logger.debug(f"Adicionando produto de nome: '{produto.nome}'")
    try:
        session = Session()
        session.add(produto)
        session.commit()
        logger.debug(f"Adicionado produto de nome: '{produto.nome}'")
        return apresenta_produto(produto), 200

    except IntegrityError as e:
        error_msg = "Produto de mesmo nome já salvo na base :/"
        logger.warning(f"Erro ao adicionar produto '{produto.nome}', {error_msg}")
        return {"mesage": error_msg}, 409

    except Exception as e:
        error_msg = "Não foi possível salvar novo item :/"
        logger.warning(f"Erro ao adicionar produto '{produto.nome}', {error_msg}")
        return {"mesage": error_msg}, 400


@app.get('/get_produtos', tags=[produto_tag],
         responses={"200": ListagemProdutosSchema, "404": ErrorSchema})
def get_produtos():
    """Faz a busca por todos os Produto cadastrados

    Retorna uma representação da listagem de produtos.
    """
    logger.debug(f"Coletando produtos ")
    session = Session()
    produtos = session.query(Produto).all()

    if not produtos:
        return {"produtos": []}, 200
    else:
        logger.debug(f"%d rodutos econtrados" % len(produtos))
        print(produtos)
        return apresenta_produtos(produtos), 200


@app.get('/get_produto', tags=[produto_tag],
         responses={"200": ProdutoViewSchema, "404": ErrorSchema})
def get_produto(query: ProdutoBuscaSchema):
    """Faz a busca por um Produto a partir do codigo do produto

    Retorna uma representação dos produtos cadastrados.
    """
    codigo = query.codigo
    logger.debug(f"Coletando dados sobre produto #{codigo}")
    session = Session()
    produto = session.query(Produto).filter(Produto.codigo == codigo).first()

    if not produto:
        error_msg = "Produto não encontrado na base :/"
        logger.warning(f"Erro ao buscar produto '{codigo}', {error_msg}")

        return {"mesage": error_msg}, 404
    else:
        logger.debug(f"Produto econtrado: '{produto.nome}'")
        
        return apresenta_produto(produto), 200


@app.get('/get_endereco', tags=[endereco_tag],
         responses={"200": EnderecoViewSchema, "404": ErrorSchema})
def get_endereco(query: EnderecoBuscaSchema):
    """Faz a busca por um Endereço a partir do CEP

    Retorna uma representação do endereço cadastrado.
    """
    cep = query.cep
    logger.debug(f"Coletando dados sobre endereço com CEP {cep}")
    
    _endereco = busca_endereco(cep)

    if not _endereco:
        error_msg = "Endereço não encontrado :/"
        logger.warning(f"Erro ao buscar endereço com CEP '{cep}', {error_msg}")

        return {"mesage": error_msg}, 404
    else:
        logger.debug(f"Endereço encontrado: '{_endereco.logradouro}'")
        
        return apresenta_endereco(_endereco), 200


@app.delete('/del_produto', tags=[produto_tag],
            responses={"200": ProdutoDelSchema, "404": ErrorSchema})
def del_produto(query: ProdutoBuscaSchema):
    """Deleta um Produto a partir do código de produto informado

    Retorna uma mensagem de confirmação da remoção.
    """
    codigo = unquote(unquote(query.codigo))
    print(codigo)
    logger.debug(f"Deletando dados sobre produto #{codigo}")
    session = Session()
    count = session.query(Produto).filter(Produto.codigo == codigo).delete()
    session.commit()

    if count:
        
        logger.debug(f"Deletado produto #{codigo}")
        return {"mesage": "Produto removido", "codigo": codigo}
    else:
        
        error_msg = "Produto não encontrado na base :/"
        logger.warning(f"Erro ao deletar produto #'{codigo}', {error_msg}")
        return {"mesage": error_msg}, 404


@app.put('/update_produto', tags=[produto_tag],
         responses={"200": ProdutoViewSchema, "404": ErrorSchema, "400": ErrorSchema})
def update_produto(form: ProdutoViewSchema):
    """Atualiza um Produto existente na base de dados

    Retorna uma representação do produto atualizado.
    """
    codigo = form.codigo
    logger.debug(f"Atualizando produto #{codigo}")
    session = Session()
    produto = session.query(Produto).filter(Produto.codigo == codigo).first()

    if not produto:
        error_msg = "Produto não encontrado na base :/"
        logger.warning(f"Erro ao atualizar produto '{codigo}', {error_msg}")
        return {"mesage": error_msg}, 404
    else:
        produto.nome = form.nome
        produto.tipo = form.tipo
        produto.valor = form.valor
        produto.descricao = form.descricao
        produto.cep = form.cep
        produto.logradouro = form.logradouro
        produto.numero = form.numero
        produto.complemento = form.complemento
        produto.bairro = form.bairro
        produto.localidade = form.localidade
        produto.uf = form.uf
        
        try:
            session.commit()
            logger.debug(f"Produto atualizado: '{produto.nome}'")
            return apresenta_produto(produto), 200
        except Exception as e:
            error_msg = "Não foi possível atualizar o produto :/"
            logger.warning(f"Erro ao atualizar produto '{produto.nome}', {error_msg}")
            return {"mesage": error_msg}, 400
