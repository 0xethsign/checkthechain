from __future__ import annotations

from ctc import rpc
from ctc import spec
from . import erc721_spec


async def async_get_erc721_total_supply(
    token: spec.Address,
    *,
    block: spec.BlockNumberReference | None = None,
) -> int:
    """get total supply of erc721 token"""
    result = await rpc.async_eth_call(
        to_address=token,
        function_abi=erc721_spec.erc721_function_abis['totalSupply'],
        block_number=block,
    )

    if not isinstance(result, int):
        raise Exception('invalid return type')

    return result


async def async_get_erc721_owner(
    token: spec.Address,
    token_id: int,
    *,
    block: spec.BlockNumberReference | None = None,
) -> spec.Address:
    """get owner of erc721 by token_id"""

    result = await rpc.async_eth_call(
        to_address=token,
        function_abi=erc721_spec.erc721_function_abis['ownerOf'],
        function_parameters=[token_id],
        block_number=block,
    )

    if not isinstance(result, str):
        raise Exception('invalid return type')

    return result


async def async_get_erc721_balance(
    token: spec.Address,
    wallet: spec.Address,
    *,
    block: spec.BlockNumberReference | None = None,
) -> int:
    """get number of erc721 tokens owner by wallet"""

    result = await rpc.async_eth_call(
        to_address=token,
        function_abi=erc721_spec.erc721_function_abis['balanceOf'],
        function_parameters=[wallet],
        block_number=block,
    )

    if not isinstance(result, int):
        raise Exception('invalid return type')

    return result


async def async_get_erc721_approved(
    token: spec.Address,
    token_id: int,
    *,
    block: spec.BlockNumberReference | None = None,
) -> spec.Address:
    """return address approved for erc721 token_id"""

    result = await rpc.async_eth_call(
        to_address=token,
        function_abi=erc721_spec.erc721_function_abis['getApproved'],
        function_parameters=[token_id],
        block_number=block,
    )

    if not isinstance(result, str):
        raise Exception('invalid return type')

    return result


async def async_get_erc721_approved_for_all(
    token: spec.Address,
    *,
    owner: spec.Address,
    operator: spec.Address,
    block: spec.BlockNumberReference | None = None,
) -> bool:
    """return whether owner has approved operator for all erc721 transfers"""

    result = await rpc.async_eth_call(
        to_address=token,
        function_abi=erc721_spec.erc721_function_abis['isApprovedForAll'],
        function_parameters=[owner, operator],
        block_number=block,
    )

    if not isinstance(result, bool):
        raise Exception('invalid return type')

    return result
