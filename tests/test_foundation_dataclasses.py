"""Foundation tests: verify core dataclasses instantiate correctly."""
import pytest
from generate.mask.models import BlockMask, MaskPattern
from generate.repair.models import AmbiguityRegion, RepairAction


def test_block_mask_instantiation():
    """T015: Verify BlockMask dataclass can be created."""
    mask = BlockMask(
        grid_size=7,
        cells={(1, 1), (2, 2), (3, 3)},
        density=3 / 49,
        pattern_id="corridor",
        attempt_index=0,
        seed=1234
    )
    
    assert mask.grid_size == 7
    assert len(mask.cells) == 3
    assert (1, 1) in mask.cells
    assert mask.pattern_id == "corridor"
    assert mask.seed == 1234


def test_block_mask_signature():
    """T015: Verify BlockMask generates stable signature."""
    mask1 = BlockMask(
        grid_size=5,
        cells={(0, 0), (1, 1), (2, 2)},
        density=0.12,
        pattern_id="test",
        attempt_index=0,
        seed=100
    )
    
    mask2 = BlockMask(
        grid_size=5,
        cells={(2, 2), (0, 0), (1, 1)},  # Different order
        density=0.12,
        pattern_id="test",
        attempt_index=0,
        seed=100
    )
    
    # Signatures should be identical (sorted)
    assert mask1.signature() == mask2.signature()


def test_mask_pattern_instantiation():
    """T015: Verify MaskPattern dataclass can be created."""
    pattern = MaskPattern(
        name="corridor",
        type="template",
        min_size=6,
        max_density=0.08,
        params={"lanes": 2, "chokepoints": 1}
    )
    
    assert pattern.name == "corridor"
    assert pattern.type == "template"
    assert pattern.min_size == 6
    assert pattern.params["lanes"] == 2


def test_ambiguity_region_instantiation():
    """T015: Verify AmbiguityRegion dataclass can be created."""
    region = AmbiguityRegion(
        cells={(3, 3), (3, 4), (4, 3)},
        divergence_count=2,
        corridor_width=3,
        distance_from_clues=5,
        score=0.85
    )
    
    assert len(region.cells) == 3
    assert region.divergence_count == 2
    assert region.score == 0.85


def test_repair_action_instantiation():
    """T015: Verify RepairAction dataclass can be created."""
    action = RepairAction(
        action_type="block",
        position=(4, 4),
        reason="High divergence frequency",
        applied=True
    )
    
    assert action.action_type == "block"
    assert action.position == (4, 4)
    assert action.applied is True


def test_repair_action_defaults():
    """T015: Verify RepairAction applied defaults to False."""
    action = RepairAction(
        action_type="clue",
        position=(2, 2),
        reason="Fallback repair"
    )
    
    assert action.applied is False
