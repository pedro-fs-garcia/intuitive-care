from contextlib import asynccontextmanager

from fastapi import FastAPI, status, Query, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, func
from sqlalchemy.orm import Session

from database import get_db, Operadora, DespesaConsolidada, DespesaAgregada, init_db
from database.db_session import engine


cors_origins = [
    "http://localhost:5173",
    "http://localhost:8080",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8080",
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    inspector = inspect(engine)
    if not inspector.has_table("operadoras"):
        print("Tabelas não encontradas. Criando tabelas...")
        init_db()
    else:
        from sqlalchemy import text
        with engine.connect() as conn:
            count = conn.execute(text("SELECT COUNT(*) FROM operadoras")).scalar()
        if count == 0:
            print("Tabelas vazias. Carregando dados...")
            init_db()
    yield


app = FastAPI(
    title="Teste Pedro Garcia",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/", tags=["Health Check"])
async def read_root() -> JSONResponse:
    content = {"name": app.title, "status": "ok"},
    return JSONResponse(content=content, status_code=status.HTTP_200_OK)


@app.get("/api/operadoras", tags=["Operadoras"])
async def list_operadoras(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    offset = (page - 1) * limit
    total_records = db.query(Operadora).count()
    operadoras = db.query(Operadora).offset(offset).limit(limit).all()

    return {
        "data": [
            {
                "cnpj": op.cnpj,
                "razao_social": op.razao_social,
                "registro_ans": op.registro_ans,
                "modalidade": op.modalidade,
                "uf": op.uf
            }
            for op in operadoras
        ],
        "total": total_records,
        "page": page,
        "limit": limit,
        "total_pages": (total_records + limit - 1) // limit
    }


@app.get("/api/operadoras/{cnpj}", tags=["Operadoras"])
async def get_operadora(cnpj: str, db: Session = Depends(get_db)):
    operadora = db.query(Operadora).filter(Operadora.cnpj == cnpj).first()

    if not operadora:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Operadora com CNPJ {cnpj} não encontrada"
        )

    return {
        "cnpj": operadora.cnpj,
        "razao_social": operadora.razao_social,
        "registro_ans": operadora.registro_ans,
        "modalidade": operadora.modalidade,
        "uf": operadora.uf
    }


@app.get("/api/operadoras/{cnpj}/despesas", tags=["Operadoras"])
async def get_operadora_despesas(
    cnpj: str,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    operadora = db.query(Operadora).filter(Operadora.cnpj == cnpj).first()

    if not operadora:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Operadora com CNPJ {cnpj} não encontrada"
        )

    offset = (page - 1) * limit

    query = (
        db.query(DespesaConsolidada)
        .filter(DespesaConsolidada.operadora_id == operadora.id)
        .order_by(DespesaConsolidada.ano.desc(), DespesaConsolidada.trimestre.desc())
    )

    total_records = query.count()
    despesas = query.offset(offset).limit(limit).all()

    return {
        "data": [
            {
                "trimestre": d.trimestre,
                "ano": d.ano,
                "valor_despesa": float(d.valor_despesa)
            }
            for d in despesas
        ],
        "operadora": {
            "cnpj": operadora.cnpj,
            "razao_social": operadora.razao_social
        },
        "total": total_records,
        "page": page,
        "limit": limit,
        "total_pages": (total_records + limit - 1) // limit
    }


@app.get("/api/estatisticas", tags=["Estatísticas"])
async def get_estatisticas(db: Session = Depends(get_db)):
    stats = db.query(
        func.sum(DespesaConsolidada.valor_despesa).label("total"),
        func.avg(DespesaConsolidada.valor_despesa).label("media"),
        func.count(DespesaConsolidada.id).label("registros")
    ).first()

    total_despesas = float(stats.total) if stats.total else 0.0
    media_despesas = float(stats.media) if stats.media else 0.0
    total_registros = stats.registros or 0

    top_operadoras = (
        db.query(
            Operadora.cnpj,
            Operadora.razao_social,
            Operadora.uf,
            func.sum(DespesaAgregada.total_despesas).label("total_despesas")
        )
        .join(DespesaAgregada, Operadora.id == DespesaAgregada.operadora_id)
        .group_by(Operadora.id)
        .order_by(func.sum(DespesaAgregada.total_despesas).desc())
        .limit(5)
        .all()
    )

    despesas_por_uf = (
        db.query(
            DespesaAgregada.uf,
            func.sum(DespesaAgregada.total_despesas).label("total"),
            func.avg(DespesaAgregada.media_trimestral).label("media_trimestral"),
            func.count(DespesaAgregada.id).label("qtd_operadoras")
        )
        .group_by(DespesaAgregada.uf)
        .order_by(func.sum(DespesaAgregada.total_despesas).desc())
        .all()
    )

    return {
        "resumo": {
            "total_despesas": total_despesas,
            "media_despesas": round(media_despesas, 2),
            "total_registros": total_registros
        },
        "top_5_operadoras": [
            {
                "cnpj": op.cnpj,
                "razao_social": op.razao_social,
                "uf": op.uf,
                "total_despesas": float(op.total_despesas) if op.total_despesas else 0.0
            }
            for op in top_operadoras
        ],
        "despesas_por_uf": [
            {
                "uf": item.uf,
                "total": float(item.total) if item.total else 0.0,
                "media_trimestral": float(item.media_trimestral) if item.media_trimestral else 0.0,
                "qtd_operadoras": item.qtd_operadoras
            }
            for item in despesas_por_uf
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.api:app", host="127.0.0.1", port=8000, reload=True)