from typing import Optional

from pydantic import BaseModel, ConfigDict


class ElementData(BaseModel):
    tagName: Optional[str] = None
    id: Optional[str] = None
    className: Optional[str] = None
    text: Optional[str] = None

    model_config = ConfigDict(extra='allow')  # Разрешаем дополнительные поля элемента


class TrackerEvent(BaseModel):
    """Модель события трекера аналитики."""
    eventType: str
    timestamp: Optional[int] = None
    sessionId: Optional[str] = None
    pageViewId: Optional[str] = None
    url: Optional[str] = None
    pathname: Optional[str] = None
    referrer: Optional[str] = None
    userAgent: Optional[str] = None
    x: Optional[int] = None
    y: Optional[int] = None
    clickType: Optional[str] = None
    element: Optional[ElementData] = None
    viewport: Optional[dict] = None
    screen: Optional[dict] = None

    model_config = ConfigDict(extra='allow')  # Разрешаем дополнительные поля для кастомных событий

