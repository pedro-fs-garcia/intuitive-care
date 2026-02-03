from sqlalchemy import String, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.db_session import Base


class Operadora(Base):
    __tablename__ = "operadoras"

    id: Mapped[int] = mapped_column(primary_key=True)
    cnpj: Mapped[str] = mapped_column(String(14), unique=True, nullable=False)
    razao_social: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    registro_ans: Mapped[str | None] = mapped_column(String(20))
    modalidade: Mapped[str | None] = mapped_column(String(100))
    uf: Mapped[str] = mapped_column(String(2), nullable=False)

    despesas_consolidadas: Mapped[list["DespesaConsolidada"]] = relationship(
        back_populates="operadora", cascade="all, delete-orphan"
    )
    despesas_agregadas: Mapped[list["DespesaAgregada"]] = relationship(
        back_populates="operadora", cascade="all, delete-orphan"
    )


class DespesaConsolidada(Base):
    __tablename__ = "despesas_consolidadas"

    id: Mapped[int] = mapped_column(primary_key=True)
    operadora_id: Mapped[int] = mapped_column(ForeignKey("operadoras.id", ondelete="CASCADE"))
    trimestre: Mapped[int] = mapped_column(nullable=False)
    ano: Mapped[int] = mapped_column(nullable=False)
    valor_despesa: Mapped[Numeric] = mapped_column(Numeric(18, 2), nullable=False)

    operadora: Mapped["Operadora"] = relationship(back_populates="despesas_consolidadas")


class DespesaAgregada(Base):
    __tablename__ = "despesas_agregadas"

    id: Mapped[int] = mapped_column(primary_key=True)
    operadora_id: Mapped[int] = mapped_column(ForeignKey("operadoras.id", ondelete="CASCADE"))
    uf: Mapped[str] = mapped_column(String(2), nullable=False)
    total_despesas: Mapped[Numeric | None] = mapped_column(Numeric(18, 2))
    media_trimestral: Mapped[Numeric | None] = mapped_column(Numeric(18, 2))
    desvio_padrao: Mapped[Numeric | None] = mapped_column(Numeric(18, 2))
    qtd_trimestres: Mapped[int | None] = mapped_column()

    operadora: Mapped["Operadora"] = relationship(back_populates="despesas_agregadas")
