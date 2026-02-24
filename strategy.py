from abc import ABC, abstractmethod
from typing import Dict, Type

from models import Order


class RiskScorer(ABC):
    """
    Abstract base class for channel-specific risk scoring strategies.

    GIVEN an Order
    WHEN score() is called
    THEN returns risk score in range [0.0, 1.0]
    """

    @abstractmethod
    def score(self, o: Order) -> float:
        """Calculate risk score for the order."""
        ...


class WebRiskScorer(RiskScorer):
    """
    Risk scoring strategy for web channel orders.

    Uses total amount as primary risk indicator.
    """

    def score(self, o: Order) -> float:
        """Score based on order total (higher total = higher risk)."""
        return min(0.99, o.total / 1000.0)


class PartnerRiskScorer(RiskScorer):
    """
    Risk scoring strategy for partner channel orders.

    Uses threshold-based risk assessment.
    """

    def score(self, o: Order) -> float:
        """Score based on $2000 threshold."""
        return 0.3 if o.total < 2000 else 0.7


class MobileRiskScorer(RiskScorer):
    """Risk scoring strategy for mobile channel orders."""

    def score(self, o: Order) -> float:
        """Mobile orders have moderate baseline risk."""
        return 0.5


# Registry pattern for extensibility
_SCORERS: Dict[str, Type[RiskScorer]] = {
    "web": WebRiskScorer,
    "partner": PartnerRiskScorer,
    "mobile": MobileRiskScorer,
}


def choose_scorer(channel: str) -> RiskScorer:
    """
    Factory function to select appropriate risk scorer.

    GIVEN a channel name
    WHEN choose_scorer is called
    THEN returns appropriate RiskScorer instance

    Raises:
        KeyError: If channel is not registered
    """
    scorer_class = _SCORERS.get(channel)
    if scorer_class is None:
        raise ValueError(f"Unknown channel: {channel}")
    return scorer_class()


def register_scorer(channel: str, scorer_class: Type[RiskScorer]) -> None:
    """
    Register a new risk scorer for a channel.

    Enables runtime extensibility without modifying core code.
    """
    _SCORERS[channel] = scorer_class
