-- HackProof Anonymized Local Development Sample Dataset
-- Contains: 10 projects, 20 contracts, 5 wasm uploads, 10 failed transactions, and timeline series

BEGIN;

-- Repositories
INSERT INTO repos (
    full_name, url, description, stars, owner, owner_avatar, owner_location, country,
    default_branch, homepage, language, license, forks, created_at, pushed_at, topics,
    discovered_via, dependencies, window_commits, base_sha, total_commits, stellar_added_in_window,
    scanned_at, declared_track
) VALUES
('ethan-r13n/nest', 'https://github.com/ethan-r13n/nest', 'Privacy-first confidential settlement vaults on Soroban', 42, 'ethan-r13n', 'https://avatars.githubusercontent.com/u/1001', 'San Francisco', 'US', 'main', 'https://nest-soroban.vercel.app', 'Rust', 'Apache-2.0', 5, '2026-10-25 09:15:00Z', '2026-10-26 11:30:00Z', ARRAY['stellar', 'soroban', 'defi', 'zk'], ARRAY['topic:soroban'], '{"rust": ["soroban-sdk", "stellar-xdr"]}', 18, 'sha001', 25, true, '2026-10-26 11:35:00Z', 'genesis'),
('0xDanomite/alloy-stellar', 'https://github.com/0xDanomite/alloy-stellar', 'High performance async contract interface toolkit for Rust', 38, '0xDanomite', 'https://avatars.githubusercontent.com/u/1002', 'London', 'GB', 'main', 'https://alloy-stellar.dev', 'Rust', 'MIT', 3, '2026-10-25 09:30:00Z', '2026-10-26 10:45:00Z', ARRAY['stellar', 'sdk', 'developer-tools'], ARRAY['topic:stellar'], '{"rust": ["soroban-sdk"]}', 14, 'sha002', 19, false, '2026-10-26 11:00:00Z', 'scale'),
('troqpay/private-yield', 'https://github.com/troqpay/private-yield', 'Shielded yield aggregator powered by Soroban smart accounts', 29, 'troqpay', 'https://avatars.githubusercontent.com/u/1003', 'Lisbon', 'PT', 'main', 'https://troqpay.xyz', 'Rust', 'Apache-2.0', 2, '2026-10-25 10:00:00Z', '2026-10-26 11:15:00Z', ARRAY['defi', 'privacy', 'soroban'], ARRAY['soroban-sdk filename:Cargo.toml'], '{"rust": ["soroban-sdk"]}', 12, 'sha003', 16, true, '2026-10-26 11:20:00Z', 'genesis'),
('hustle1hustle/bookerbob-hackmeridian-2026', 'https://github.com/hustle1hustle/bookerbob-hackmeridian-2026', 'Decentralized appointment escrow and calendar collateral', 24, 'hustle1hustle', 'https://avatars.githubusercontent.com/u/1004', 'Berlin', 'DE', 'main', 'https://bookerbob.io', 'TypeScript', 'MIT', 1, '2026-10-25 10:30:00Z', '2026-10-26 09:50:00Z', ARRAY['hackmeridian', 'freighter'], ARRAY['freighter in:description,readme'], '{"js": ["@stellar/stellar-sdk"]}', 9, 'sha004', 12, true, '2026-10-26 10:00:00Z', 'genesis'),
('ygk94/4ward', 'https://github.com/ygk94/4ward', 'Cross-border payroll streaming with programmable milestones', 31, 'ygk94', 'https://avatars.githubusercontent.com/u/1005', 'Seoul', 'KR', 'main', 'https://4ward.finance', 'TypeScript', 'MIT', 4, '2026-10-25 11:00:00Z', '2026-10-26 11:40:00Z', ARRAY['payroll', 'soroban', 'defi'], ARRAY['topic:soroban'], '{"rust": ["soroban-sdk"], "js": ["@stellar/stellar-sdk"]}', 15, 'sha005', 22, true, '2026-10-26 11:45:00Z', 'genesis'),
('enzoblain/ZKross', 'https://github.com/enzoblain/ZKross', 'Zero-knowledge cross-chain liquidity intent bridge', 45, 'enzoblain', 'https://avatars.githubusercontent.com/u/1006', 'Paris', 'FR', 'main', 'https://zkross.network', 'Rust', 'Apache-2.0', 7, '2026-10-25 11:30:00Z', '2026-10-26 11:55:00Z', ARRAY['zk', 'cross-chain', 'intents'], ARRAY['soroban in:name,description,readme,topics'], '{"rust": ["soroban-sdk"]}', 21, 'sha006', 30, true, '2026-10-26 12:00:00Z', 'scale'),
('stellar-sentinel/sentinel-contracts', 'https://github.com/stellar-sentinel/sentinel-contracts', 'Automated smart contract monitoring and circuit breakers', 19, 'stellar-sentinel', 'https://avatars.githubusercontent.com/u/1007', 'Austin', 'US', 'main', 'https://sentinel.stellar.io', 'Rust', 'MIT', 1, '2026-10-25 12:00:00Z', '2026-10-26 08:30:00Z', ARRAY['security', 'monitoring', 'soroban'], ARRAY['topic:soroban'], '{"rust": ["soroban-sdk"]}', 8, 'sha007', 10, true, '2026-10-26 08:40:00Z', 'genesis'),
('lumina-defi/lumina-vaults', 'https://github.com/lumina-defi/lumina-vaults', 'Dynamic collateral vaults and debt management protocol', 22, 'lumina-defi', 'https://avatars.githubusercontent.com/u/1008', 'Toronto', 'CA', 'main', 'https://lumina.fi', 'Rust', 'MIT', 2, '2026-10-25 12:45:00Z', '2026-10-26 10:10:00Z', ARRAY['vaults', 'lending', 'soroban'], ARRAY['soroban-sdk filename:Cargo.toml'], '{"rust": ["soroban-sdk"]}', 11, 'sha008', 15, true, '2026-10-26 10:15:00Z', 'genesis'),
('soroforge/soroforge-indexer', 'https://github.com/soroforge/soroforge-indexer', 'Sub-second event indexing pipeline for Soroban ledger changes', 34, 'soroforge', 'https://avatars.githubusercontent.com/u/1009', 'Munich', 'DE', 'main', 'https://soroforge.xyz', 'Go', 'Apache-2.0', 3, '2026-10-25 13:00:00Z', '2026-10-26 11:25:00Z', ARRAY['indexer', 'infra', 'stellar'], ARRAY['github.com/stellar/go filename:go.mod'], '{"go": ["github.com/stellar/go"]}', 16, 'sha009', 28, false, '2026-10-26 11:30:00Z', 'scale'),
('aurora-dex/aurora-soroban', 'https://github.com/aurora-dex/aurora-soroban', 'Concentrated liquidity automated market maker for Stellar tokens', 28, 'aurora-dex', 'https://avatars.githubusercontent.com/u/1010', 'Amsterdam', 'NL', 'main', 'https://auroradex.exchange', 'Rust', 'Apache-2.0', 3, '2026-10-25 13:30:00Z', '2026-10-26 11:05:00Z', ARRAY['amm', 'dex', 'liquidity'], ARRAY['topic:soroban'], '{"rust": ["soroban-sdk"]}', 13, 'sha010', 18, true, '2026-10-26 11:10:00Z', 'genesis')
ON CONFLICT (full_name) DO NOTHING;

-- Projects
INSERT INTO projects (
    project_id, full_name, footprint, tier, contracts, classic_ops, assets,
    wasm_uploads, failed_txs, builders, first_activity, last_activity
) VALUES
('repo:ethan-r13n/nest', 'ethan-r13n/nest', 'contracts,wasm,accounts', 'verified', 3, 4, 1, 1, 1, 2, '2026-10-25 09:20:00Z', '2026-10-26 11:30:00Z'),
('repo:0xDanomite/alloy-stellar', '0xDanomite/alloy-stellar', 'contracts,wasm', 'verified', 2, 2, 0, 1, 0, 1, '2026-10-25 09:35:00Z', '2026-10-26 10:45:00Z'),
('repo:troqpay/private-yield', 'troqpay/private-yield', 'contracts,wasm', 'verified', 2, 1, 0, 1, 2, 1, '2026-10-25 10:10:00Z', '2026-10-26 11:15:00Z'),
('repo:hustle1hustle/bookerbob-hackmeridian-2026', 'hustle1hustle/bookerbob-hackmeridian-2026', 'contracts,wasm', 'verified', 2, 0, 0, 1, 1, 1, '2026-10-25 10:35:00Z', '2026-10-26 09:50:00Z'),
('repo:ygk94/4ward', 'ygk94/4ward', 'contracts,wasm,accounts', 'verified', 3, 3, 1, 1, 0, 2, '2026-10-25 11:05:00Z', '2026-10-26 11:40:00Z'),
('repo:enzoblain/ZKross', 'enzoblain/ZKross', 'contracts,wasm', 'verified', 3, 2, 0, 1, 1, 2, '2026-10-25 11:35:00Z', '2026-10-26 11:55:00Z'),
('repo:stellar-sentinel/sentinel-contracts', 'stellar-sentinel/sentinel-contracts', 'contracts,wasm', 'verified', 1, 0, 0, 1, 0, 1, '2026-10-25 12:10:00Z', '2026-10-26 08:30:00Z'),
('repo:lumina-defi/lumina-vaults', 'lumina-defi/lumina-vaults', 'contracts,wasm', 'verified', 2, 1, 0, 1, 1, 1, '2026-10-25 12:50:00Z', '2026-10-26 10:10:00Z'),
('repo:soroforge/soroforge-indexer', 'soroforge/soroforge-indexer', 'accounts', 'likely', 0, 6, 0, 0, 0, 1, '2026-10-25 13:10:00Z', '2026-10-26 11:25:00Z'),
('repo:aurora-dex/aurora-soroban', 'aurora-dex/aurora-soroban', 'contracts,wasm', 'verified', 2, 1, 0, 1, 2, 1, '2026-10-25 13:35:00Z', '2026-10-26 11:05:00Z')
ON CONFLICT (project_id) DO NOTHING;

-- Contributors
INSERT INTO repo_contributors (full_name, login, url, avatar_url, contributions) VALUES
('ethan-r13n/nest', 'ethan-r13n', 'https://github.com/ethan-r13n', 'https://avatars.githubusercontent.com/u/1001', 12),
('ethan-r13n/nest', 'alice-builder', 'https://github.com/alice-builder', 'https://avatars.githubusercontent.com/u/1011', 6),
('0xDanomite/alloy-stellar', '0xDanomite', 'https://github.com/0xDanomite', 'https://avatars.githubusercontent.com/u/1002', 14),
('troqpay/private-yield', 'troqpay', 'https://github.com/troqpay', 'https://avatars.githubusercontent.com/u/1003', 12),
('hustle1hustle/bookerbob-hackmeridian-2026', 'hustle1hustle', 'https://github.com/hustle1hustle', 'https://avatars.githubusercontent.com/u/1004', 9),
('ygk94/4ward', 'ygk94', 'https://github.com/ygk94', 'https://avatars.githubusercontent.com/u/1005', 11),
('ygk94/4ward', 'bob-builder', 'https://github.com/bob-builder', 'https://avatars.githubusercontent.com/u/1012', 4),
('enzoblain/ZKross', 'enzoblain', 'https://github.com/enzoblain', 'https://avatars.githubusercontent.com/u/1006', 15),
('enzoblain/ZKross', 'charlie-zk', 'https://github.com/charlie-zk', 'https://avatars.githubusercontent.com/u/1013', 6),
('stellar-sentinel/sentinel-contracts', 'stellar-sentinel', 'https://github.com/stellar-sentinel', 'https://avatars.githubusercontent.com/u/1007', 8),
('lumina-defi/lumina-vaults', 'lumina-defi', 'https://github.com/lumina-defi', 'https://avatars.githubusercontent.com/u/1008', 11),
('soroforge/soroforge-indexer', 'soroforge', 'https://github.com/soroforge', 'https://avatars.githubusercontent.com/u/1009', 16),
('aurora-dex/aurora-soroban', 'aurora-dex', 'https://github.com/aurora-dex', 'https://avatars.githubusercontent.com/u/1010', 13)
ON CONFLICT (full_name, login) DO NOTHING;

-- 20 Contracts Across The Window
INSERT INTO contracts (contract_id, deployer, wasm_hash, tx_hash, ledger, deployed_at) VALUES
('CAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0001', 'GAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0001', 'wasmhash0001', 'txdeploy0001', 10001, '2026-10-25 09:20:00Z'),
('CAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0002', 'GAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0001', 'wasmhash0001', 'txdeploy0002', 10012, '2026-10-25 09:40:00Z'),
('CAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0003', 'GAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0001', 'wasmhash0002', 'txdeploy0003', 10034, '2026-10-25 10:15:00Z'),
('CAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0004', 'GAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0002', 'wasmhash0003', 'txdeploy0004', 10055, '2026-10-25 10:40:00Z'),
('CAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0005', 'GAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0002', 'wasmhash0003', 'txdeploy0005', 10080, '2026-10-25 11:20:00Z'),
('CAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0006', 'GAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0003', 'wasmhash0004', 'txdeploy0006', 10105, '2026-10-25 12:00:00Z'),
('CAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0007', 'GAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0003', 'wasmhash0004', 'txdeploy0007', 10140, '2026-10-25 13:10:00Z'),
('CAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0008', 'GAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0004', 'wasmhash0005', 'txdeploy0008', 10185, '2026-10-25 14:25:00Z'),
('CAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0009', 'GAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0004', 'wasmhash0005', 'txdeploy0009', 10220, '2026-10-25 15:30:00Z'),
('CAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0010', 'GAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0005', 'wasmhash0006', 'txdeploy0010', 10260, '2026-10-25 16:45:00Z'),
('CAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0011', 'GAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0005', 'wasmhash0006', 'txdeploy0011', 10300, '2026-10-25 18:00:00Z'),
('CAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0012', 'GAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0005', 'wasmhash0007', 'txdeploy0012', 10340, '2026-10-25 19:15:00Z'),
('CAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0013', 'GAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0006', 'wasmhash0008', 'txdeploy0013', 10385, '2026-10-25 21:00:00Z'),
('CAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0014', 'GAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0006', 'wasmhash0008', 'txdeploy0014', 10420, '2026-10-25 22:30:00Z'),
('CAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0015', 'GAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0006', 'wasmhash0009', 'txdeploy0015', 10465, '2026-10-26 01:10:00Z'),
('CAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0016', 'GAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0007', 'wasmhash0010', 'txdeploy0016', 10510, '2026-10-26 04:00:00Z'),
('CAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0017', 'GAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0008', 'wasmhash0011', 'txdeploy0017', 10555, '2026-10-26 06:20:00Z'),
('CAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0018', 'GAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0008', 'wasmhash0011', 'txdeploy0018', 10590, '2026-10-26 08:40:00Z'),
('CAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0019', 'GAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0010', 'wasmhash0012', 'txdeploy0019', 10630, '2026-10-26 09:30:00Z'),
('CAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0020', 'GAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0010', 'wasmhash0012', 'txdeploy0020', 10675, '2026-10-26 11:00:00Z')
ON CONFLICT (contract_id) DO NOTHING;

-- Contract Attribution Links
INSERT INTO links (full_name, subject_kind, subject, method) VALUES
('ethan-r13n/nest', 'contract', 'CAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0001', 'contract_in_repo'),
('ethan-r13n/nest', 'contract', 'CAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0002', 'contract_in_repo'),
('ethan-r13n/nest', 'contract', 'CAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0003', 'deployer_in_repo'),
('0xDanomite/alloy-stellar', 'contract', 'CAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0004', 'contract_in_repo'),
('0xDanomite/alloy-stellar', 'contract', 'CAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0005', 'deployer_in_repo'),
('troqpay/private-yield', 'contract', 'CAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0006', 'contract_in_repo'),
('troqpay/private-yield', 'contract', 'CAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0007', 'contract_in_repo'),
('hustle1hustle/bookerbob-hackmeridian-2026', 'contract', 'CAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0008', 'contract_in_repo'),
('hustle1hustle/bookerbob-hackmeridian-2026', 'contract', 'CAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0009', 'deployer_in_repo'),
('ygk94/4ward', 'contract', 'CAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0010', 'contract_in_repo'),
('ygk94/4ward', 'contract', 'CAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0011', 'contract_in_repo'),
('ygk94/4ward', 'contract', 'CAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0012', 'deployer_in_repo'),
('enzoblain/ZKross', 'contract', 'CAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0013', 'contract_in_repo'),
('enzoblain/ZKross', 'contract', 'CAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0014', 'contract_in_repo'),
('enzoblain/ZKross', 'contract', 'CAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0015', 'deployer_in_repo'),
('stellar-sentinel/sentinel-contracts', 'contract', 'CAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0016', 'contract_in_repo'),
('lumina-defi/lumina-vaults', 'contract', 'CAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0017', 'contract_in_repo'),
('lumina-defi/lumina-vaults', 'contract', 'CAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0018', 'contract_in_repo'),
('aurora-dex/aurora-soroban', 'contract', 'CAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0019', 'contract_in_repo'),
('aurora-dex/aurora-soroban', 'contract', 'CAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0020', 'contract_in_repo')
ON CONFLICT (subject_kind, subject, full_name) DO NOTHING;

-- Failed Transactions
INSERT INTO failed_txs (tx_hash, source_account, kind, result_code, ledger, created_at) VALUES
('txfail0001', 'GAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0001', 'invoke', 'TRAPPED', 10020, '2026-10-25 09:30:00Z'),
('txfail0002', 'GAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0003', 'invoke', 'INSUFFICIENT_REFUNDABLE_FEE', 10090, '2026-10-25 11:45:00Z'),
('txfail0003', 'GAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0003', 'invoke', 'RESOURCE_LIMIT_EXCEEDED', 10120, '2026-10-25 12:30:00Z'),
('txfail0004', 'GAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0004', 'invoke', 'ENTRY_ARCHIVED', 10190, '2026-10-25 14:40:00Z'),
('txfail0005', 'GAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0006', 'invoke', 'TRAPPED', 10400, '2026-10-25 21:40:00Z'),
('txfail0006', 'GAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0008', 'invoke', 'MALFORMED', 10570, '2026-10-26 07:15:00Z'),
('txfail0007', 'GAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0010', 'invoke', 'TRAPPED', 10640, '2026-10-26 09:50:00Z'),
('txfail0008', 'GAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0010', 'invoke', 'INSUFFICIENT_REFUNDABLE_FEE', 10660, '2026-10-26 10:20:00Z')
ON CONFLICT (tx_hash) DO NOTHING;

COMMIT;
