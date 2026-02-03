from fastapi import FastAPI, status, Query, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import get_db, Operadora, DespesaConsolidada, DespesaAgregada


def init_routes(app: FastAPI) -> None:

    @app.get("/", tags=["Health Check"])
    async def read_root() -> JSONResponse:
        content = {"name": app.title, "status": "ok"}
        return JSONResponse(content=content, status_code=status.HTTP_200_OK)


    @app.get("/api/operadoras", tags=["Operadoras"])
    async def list_operadoras(
        page: int = Query(1, ge=1),
        limit: int = Query(10, ge=1, le=100),
        search: str = Query("", description="Busca por razão social ou CNPJ"),
        db: Session = Depends(get_db)
    ):
        offset = (page - 1) * limit
        
        query = db.query(Operadora)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (Operadora.razao_social.ilike(search_term)) |
                (Operadora.cnpj.ilike(search_term))
            )
        
        total_records = query.count()
        operadoras = query.offset(offset).limit(limit).all()

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

        # Os dados são YTD (acumulados). Calcular valor isolado do trimestre.
        from sqlalchemy import text
        
        query_despesas = text("""
            WITH despesas_isoladas AS (
                SELECT 
                    id,
                    operadora_id,
                    ano,
                    trimestre,
                    valor_despesa AS valor_ytd,
                    valor_despesa - COALESCE(
                        LAG(valor_despesa) OVER (PARTITION BY operadora_id, ano ORDER BY trimestre),
                        0
                    ) AS valor_isolado
                FROM despesas_consolidadas
            )
            SELECT ano, trimestre, valor_ytd, valor_isolado
            FROM despesas_isoladas
            WHERE operadora_id = :operadora_id
            ORDER BY ano DESC, trimestre DESC
            LIMIT :limit OFFSET :offset
        """)
        
        query_count = text("""
            SELECT COUNT(*) as total
            FROM despesas_consolidadas
            WHERE operadora_id = :operadora_id
        """)
        
        offset = (page - 1) * limit
        
        total_result = db.execute(query_count, {"operadora_id": operadora.id}).fetchone()
        total_records = total_result.total if total_result else 0
        
        despesas = db.execute(query_despesas, {
            "operadora_id": operadora.id,
            "limit": limit,
            "offset": offset
        }).fetchall()

        return {
            "data": [
                {
                    "trimestre": d.trimestre,
                    "ano": d.ano,
                    "valor_despesa": float(d.valor_isolado),  # Valor isolado do trimestre
                    "valor_ytd": float(d.valor_ytd)  # Valor acumulado (YTD) para referência
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
        # Usamos despesas_agregadas que já tem valores desacumulados pelo ETL
        stats = db.query(
            func.sum(DespesaAgregada.total_despesas).label("total"),
            func.avg(DespesaAgregada.media_trimestral).label("media"),
            func.count(DespesaAgregada.id).label("registros")
        ).first()
        
        total_despesas = float(stats.total) if stats and stats.total else 0.0
        media_despesas = float(stats.media) if stats and stats.media else 0.0
        total_registros = stats.registros if stats else 0

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
    
    @app.get("/api/estatisticas-complementares", tags=["Estatísticas"])
    async def get_estatisticas_complementares(db: Session = Depends(get_db)):
        """
        Estatísticas analíticas complementares (Item 3.4 do teste):
        - Query 1: Top 5 operadoras com maior crescimento percentual
        - Query 2: Distribuição de despesas por UF (top 5)
        - Query 3: Operadoras acima da média em 2+ trimestres
        """
        
        # Query 1: Top 5 operadoras com maior crescimento percentual
        # ATENÇÃO: Os dados são YTD (acumulados por ano). Precisamos desacumular.
        from sqlalchemy import text
        
        query_crescimento = text("""
            WITH despesas_isoladas AS (
                SELECT 
                    operadora_id,
                    ano,
                    trimestre,
                    valor_despesa - COALESCE(
                        LAG(valor_despesa) OVER (PARTITION BY operadora_id, ano ORDER BY trimestre),
                        0
                    ) AS valor_isolado
                FROM despesas_consolidadas
            ),
            periodo AS (
                SELECT
                    MIN(ano * 10 + trimestre) AS primeiro_periodo,
                    MAX(ano * 10 + trimestre) AS ultimo_periodo
                FROM despesas_consolidadas
            ),
            despesas_primeiro AS (
                SELECT di.operadora_id, di.valor_isolado
                FROM despesas_isoladas di
                CROSS JOIN periodo p
                WHERE di.ano * 10 + di.trimestre = p.primeiro_periodo
            ),
            despesas_ultimo AS (
                SELECT di.operadora_id, di.valor_isolado
                FROM despesas_isoladas di
                CROSS JOIN periodo p
                WHERE di.ano * 10 + di.trimestre = p.ultimo_periodo
            )
            SELECT
                o.cnpj,
                o.razao_social,
                dp.valor_isolado AS despesa_inicial,
                du.valor_isolado AS despesa_final,
                ROUND(
                    ((du.valor_isolado - dp.valor_isolado) / NULLIF(dp.valor_isolado, 0)) * 100,
                    2
                ) AS crescimento_percentual
            FROM despesas_primeiro dp
            INNER JOIN despesas_ultimo du ON dp.operadora_id = du.operadora_id
            INNER JOIN operadoras o ON o.id = dp.operadora_id
            WHERE dp.valor_isolado > 0
            ORDER BY crescimento_percentual DESC
            LIMIT 5
        """)
        
        resultado_crescimento = db.execute(query_crescimento).fetchall()
        top_crescimento = [
            {
                "cnpj": row.cnpj,
                "razao_social": row.razao_social,
                "despesa_inicial": float(row.despesa_inicial) if row.despesa_inicial else 0.0,
                "despesa_final": float(row.despesa_final) if row.despesa_final else 0.0,
                "crescimento_percentual": float(row.crescimento_percentual) if row.crescimento_percentual else 0.0
            }
            for row in resultado_crescimento
        ]
        
        # Query 2: Distribuição de despesas por UF (top 5) - usando valores desacumulados
        query_uf = text("""
            WITH despesas_isoladas AS (
                SELECT 
                    operadora_id,
                    ano,
                    trimestre,
                    valor_despesa - COALESCE(
                        LAG(valor_despesa) OVER (PARTITION BY operadora_id, ano ORDER BY trimestre),
                        0
                    ) AS valor_isolado
                FROM despesas_consolidadas
            )
            SELECT
                o.uf,
                COUNT(DISTINCT o.id) AS qtd_operadoras,
                SUM(di.valor_isolado) AS total_despesas,
                ROUND(AVG(di.valor_isolado), 2) AS media_por_registro,
                ROUND(SUM(di.valor_isolado) / NULLIF(COUNT(DISTINCT o.id), 0), 2) AS media_por_operadora
            FROM despesas_isoladas di
            INNER JOIN operadoras o ON o.id = di.operadora_id
            WHERE di.valor_isolado > 0
            GROUP BY o.uf
            ORDER BY total_despesas DESC
            LIMIT 5
        """)
        
        resultado_uf = db.execute(query_uf).fetchall()
        top_uf = [
            {
                "uf": row.uf,
                "qtd_operadoras": row.qtd_operadoras,
                "total_despesas": float(row.total_despesas) if row.total_despesas else 0.0,
                "media_por_registro": float(row.media_por_registro) if row.media_por_registro else 0.0,
                "media_por_operadora": float(row.media_por_operadora) if row.media_por_operadora else 0.0
            }
            for row in resultado_uf
        ]
        
        # Query 3: Operadoras acima da média em 2+ trimestres - usando valores desacumulados
        query_acima_media = text("""
            WITH despesas_isoladas AS (
                SELECT 
                    operadora_id,
                    ano,
                    trimestre,
                    valor_despesa - COALESCE(
                        LAG(valor_despesa) OVER (PARTITION BY operadora_id, ano ORDER BY trimestre),
                        0
                    ) AS valor_isolado
                FROM despesas_consolidadas
            ),
            media_geral AS (
                SELECT AVG(valor_isolado) AS media
                FROM despesas_isoladas
                WHERE valor_isolado > 0
            ),
            trimestres_acima_media AS (
                SELECT
                    di.operadora_id,
                    COUNT(*) AS trimestres_acima
                FROM despesas_isoladas di
                CROSS JOIN media_geral mg
                WHERE di.valor_isolado > mg.media
                GROUP BY di.operadora_id
            )
            SELECT 
                COUNT(*) AS total_operadoras,
                (SELECT media FROM media_geral) AS media_geral
            FROM trimestres_acima_media
            WHERE trimestres_acima >= 2
        """)
        
        resultado_acima_media = db.execute(query_acima_media).fetchone()
        
        return {
            "top_5_crescimento": top_crescimento,
            "top_5_uf": top_uf,
            "operadoras_acima_media": {
                "total": resultado_acima_media.total_operadoras if resultado_acima_media else 0,
                "media_geral_referencia": float(resultado_acima_media.media_geral) if resultado_acima_media and resultado_acima_media.media_geral else 0.0,
                "criterio": "Despesas acima da média geral em pelo menos 2 dos 3 trimestres"
            }
        }