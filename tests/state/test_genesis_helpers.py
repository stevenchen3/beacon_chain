from beacon_chain.utils.blake import blake
from beacon_chain.utils.simpleserialize import (
    serialize,
)

from beacon_chain.state.constants import (
    ZERO_HASH32,
)
from beacon_chain.state.genesis_helpers import (
    get_genesis_active_state,
    get_genesis_block,
    get_genesis_crystallized_state,
)


def test_get_genesis_active_state(config):
    active_state = get_genesis_active_state(config)
    assert active_state.num_pending_attestations == 0
    assert active_state.num_recent_block_hashes == config['cycle_length'] * 2


def test_get_genesis_crystallized_state(genesis_validators,
                                        init_shuffling_seed,
                                        config):
    crystallized_state = get_genesis_crystallized_state(
        genesis_validators,
        init_shuffling_seed,
        config,
    )
    len_indices_for_slots = config['cycle_length'] * 2
    total_deposits = config['deposit_size'] * len(genesis_validators)

    assert crystallized_state.validators == genesis_validators
    assert crystallized_state.last_state_recalc == 0
    assert len(crystallized_state.indices_for_slots) == len_indices_for_slots
    assert crystallized_state.last_justified_slot == 0
    assert crystallized_state.justified_streak == 0
    assert crystallized_state.last_finalized_slot == 0
    assert crystallized_state.current_dynasty == 1
    assert crystallized_state.crosslinking_start_shard == 0
    assert len(crystallized_state.crosslink_records) == config['shard_count']
    for crosslink in crystallized_state.crosslink_records:
        assert crosslink.hash == ZERO_HASH32
        assert crosslink.slot == 0
        assert crosslink.dynasty == 0
    assert crystallized_state.total_deposits == total_deposits
    assert crystallized_state.dynasty_seed == init_shuffling_seed
    assert crystallized_state.dynasty_seed_last_reset == 1


def test_get_genesis_block(genesis_active_state, genesis_crystallized_state):
    active_state_root = blake(serialize(genesis_active_state))
    crystallized_state_root = blake(serialize(genesis_crystallized_state))

    block = get_genesis_block(
        active_state_root=active_state_root,
        crystallized_state_root=crystallized_state_root,
    )

    assert block.parent_hash == ZERO_HASH32
    assert block.slot_number == 0
    assert block.randao_reveal == ZERO_HASH32
    assert block.num_attestations == 0
    assert block.pow_chain_ref == ZERO_HASH32
    assert block.active_state_root == active_state_root
    assert block.crystallized_state_root == crystallized_state_root
