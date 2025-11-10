"""Strategy registry for staged uniqueness validation."""

from typing import Dict, List, Callable
from generate.uniqueness_staged.result import StrategyProfile


# Global registry of available strategies
_STRATEGY_REGISTRY: Dict[str, StrategyProfile] = {}


def register_strategy(profile: StrategyProfile) -> None:
    """Register a uniqueness checking strategy.
    
    Args:
        profile: Strategy configuration to register
        
    Raises:
        ValueError: If strategy ID already registered
    """
    if profile.id in _STRATEGY_REGISTRY:
        raise ValueError(f"Strategy '{profile.id}' already registered")
    
    _STRATEGY_REGISTRY[profile.id] = profile


def get_strategy(strategy_id: str) -> StrategyProfile:
    """Get a registered strategy by ID.
    
    Args:
        strategy_id: Unique strategy identifier
        
    Returns:
        Strategy profile
        
    Raises:
        KeyError: If strategy not found
    """
    if strategy_id not in _STRATEGY_REGISTRY:
        raise KeyError(f"Strategy '{strategy_id}' not registered")
    
    return _STRATEGY_REGISTRY[strategy_id]


def list_strategies() -> List[StrategyProfile]:
    """List all registered strategies in stable order.
    
    Returns:
        List of strategy profiles sorted by ID for determinism
    """
    return [_STRATEGY_REGISTRY[key] for key in sorted(_STRATEGY_REGISTRY.keys())]


def clear_registry() -> None:
    """Clear all registered strategies (mainly for testing)."""
    _STRATEGY_REGISTRY.clear()


# Register default heuristic profiles
def _register_defaults():
    """Register default heuristic profiles for early-exit stage."""
    
    # Row-major position ordering
    register_strategy(StrategyProfile(
        id='row_major',
        budget_share=0.0,  # Allocated dynamically
        params={'position_order': 'row_major', 'value_order': 'ascending'},
        capabilities={'detect_non_unique'}
    ))
    
    # Center-out position ordering
    register_strategy(StrategyProfile(
        id='center_out',
        budget_share=0.0,
        params={'position_order': 'center_out', 'value_order': 'ascending'},
        capabilities={'detect_non_unique'}
    ))
    
    # Minimum remaining values (MRV) heuristic
    register_strategy(StrategyProfile(
        id='mrv',
        budget_share=0.0,
        params={'position_order': 'mrv', 'value_order': 'ascending'},
        capabilities={'detect_non_unique'}
    ))
    
    # Degree-biased ordering
    register_strategy(StrategyProfile(
        id='degree_biased',
        budget_share=0.0,
        params={'position_order': 'degree', 'value_order': 'ascending'},
        capabilities={'detect_non_unique'}
    ))


# Initialize default strategies on module import
_register_defaults()
