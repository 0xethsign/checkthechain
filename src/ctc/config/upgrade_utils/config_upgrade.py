from __future__ import annotations

import sys
import typing

import ctc
from ctc import spec
from .. import config_defaults
from . import version_utils


def upgrade_config(
    old_config: typing.MutableMapping[typing.Any, typing.Any]
) -> typing.MutableMapping[str, typing.Any]:
    """upgrade config to latest version as much as possible"""

    # detect version
    version = old_config.get('config_spec_version')
    if version is None:
        version = old_config.get('version')

    # perform upgrade
    if not isinstance(version, str):
        print(
            'old_config has unknown version, using default config',
            file=sys.stderr,
        )
        return dict(config_defaults.get_default_config())

    new_config = old_config
    config_version = version
    if not (
        config_version.startswith('0.2.')
        or config_version.startswith('0.3.0')
        or config_version.startswith('0.3.1')
    ):
        raise Exception('invalid config version')

    # update config from old version using upgrade path
    upgrade_functions = {
        '0.2.': upgrade__0_2_0__to__0_3_0,
        '0.3.0': upgrade__0_3_0__to__0_3_1,
    }
    for from_version, upgrade_function in upgrade_functions.items():
        if config_version.startswith(from_version):
            new_config = upgrade_function(new_config)
            config_version = new_config['config_spec_version']

    new_config_stable = version_utils.get_stable_version(
        new_config['config_spec_version']
    )
    ctc_stable = version_utils.get_stable_version(ctc.__version__)
    if (
        new_config_stable == ctc_stable
        and new_config['config_spec_version'] != ctc.__version__
    ):
        new_config['config_spec_version'] = ctc.__version__

    return new_config

    # # ? perform validation


def upgrade__0_2_0__to__0_3_0(
    old_config: typing.MutableMapping[typing.Any, typing.Any]
) -> typing.MutableMapping[typing.Any, typing.Any]:

    upgraded = dict(old_config)
    network_defaults = upgraded.pop('network_defaults', {})
    upgraded['default_network'] = network_defaults.get('default_network')
    upgraded['default_providers'] = network_defaults.get(
        'default_providers', {}
    )

    # add default networks
    upgraded['networks'] = dict(upgraded.get('networks', {}))
    default_networks = config_defaults.get_default_networks_metadata()
    for chain_id, network_metadata in default_networks.items():
        name = network_metadata['name']
        if name not in upgraded['networks']:
            upgraded['networks'][name] = network_metadata

    # convert to integer network references
    chain_ids_by_network_name = {
        network_metadata['name']: network_metadata['chain_id']
        for network_name, network_metadata in upgraded['networks'].items()
    }
    upgraded['networks'] = {
        chain_ids_by_network_name[network_name]: network_metadata
        for network_name, network_metadata in upgraded['networks'].items()
    }

    if upgraded['default_network'] not in chain_ids_by_network_name:
        raise spec.ConfigUpgradeError(
            'unknown chain_id for network ' + str(upgraded['default_network'])
        )
    upgraded['default_network'] = chain_ids_by_network_name[
        upgraded['default_network']
    ]
    upgraded['default_providers'] = {
        chain_ids_by_network_name[network_name]: provider_name
        for network_name, provider_name in upgraded['default_providers'].items()
    }

    # set provider network references to chain_id's instead of network names
    new_providers = {}
    for provider_name, provider in upgraded['providers'].items():
        new_providers[provider_name] = dict(provider)
        old_network = new_providers[provider_name].get('network')
        if isinstance(old_network, str):
            new_providers[provider_name]['network'] = chain_ids_by_network_name[
                old_network
            ]
    upgraded['providers'] = new_providers

    # set db config
    default_db_config = config_defaults.get_default_db_config(
        data_dir=old_config['data_dir']
    )
    upgraded['db_configs'] = {'main': default_db_config}

    upgraded['log_rpc_calls'] = True
    upgraded['log_sql_queries'] = True

    # set new version
    if 'version' in upgraded:
        del upgraded['version']
    upgraded['config_spec_version'] = '0.3.0'

    return upgraded


def upgrade__0_3_0__to__0_3_1(
    old_config: typing.MutableMapping[typing.Any, typing.Any]
) -> typing.MutableMapping[typing.Any, typing.Any]:

    upgraded = dict(old_config)
    if 'cli_color_theme' not in upgraded:
        upgraded[
            'cli_color_theme'
        ] = config_defaults.get_default_cli_color_theme()
    if 'cli_chart_charset' not in upgraded:
        upgraded[
            'cli_chart_charset'
        ] = config_defaults.get_default_cli_chart_charset()
    upgraded['config_spec_version'] = '0.3.1'

    return upgraded


def omit_extra_version_data(version: str) -> str:
    for substr in ['a', 'b', 'rc']:
        if substr in version:
            index = version.index(substr)
            version = version[:index]
    return version
