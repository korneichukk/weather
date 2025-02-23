from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from typing import Dict, Any


class Base(DeclarativeBase):
    pass


class City(Base):
    __tablename__ = "cities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    city: Mapped[str] = mapped_column(String(255))
    city_ascii: Mapped[str] = mapped_column(String(255))
    lat: Mapped[float] = mapped_column(Float(precision=4))
    lng: Mapped[float] = mapped_column(Float(precision=4))
    country: Mapped[str] = mapped_column(String(255))
    admin_name: Mapped[str] = mapped_column(String(255))
    region: Mapped[str] = mapped_column(String(255), nullable=True)

    def __repr__(self) -> str:
        return f"City(city={self.city}, lat={self.lat}, lng={self.lng}, region={self.region})"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "city": self.city,
            "city_ascii": self.city_ascii,
            "lat": self.lat,
            "lng": self.lng,
            "country": self.country,
            "admin_name": self.admin_name,
            "region": self.region,
        }
