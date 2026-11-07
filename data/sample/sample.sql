-- HackProof anonymized sample dataset (10 projects, 20 contracts, 27-hour window)
-- Contains only public GitHub handles and public testnet contract metadata.

INSERT INTO repos (
    full_name, url, description, stars, owner, owner_avatar, owner_location, country,
    default_branch, homepage, language, license, forks, created_at, pushed_at,
    topics, discovered_via, dependencies, window_commits, base_sha, total_commits,
    stellar_added_in_window, scanned_at, declared_track
) VALUES
    ('ethan-r13n/nest', 'https://github.com/ethan-r13n/nest', 'Self-custodial savings vaults on Soroban', 12, 'ethan-r13n', NULL, NULL, NULL, 'main', 'https://nest-stellar.vercel.app', 'Rust', 'MIT', 2, '2026-10-25T09:15:00Z', '2026-10-26T11:30:00Z', ARRAY['stellar', 'soroban'], ARRAY['search'], '{"ecosystems": ["rust", "js"], "packages": {"soroban-sdk": "22.0.0", "@stellar/stellar-sdk": "13.0.0"}}'::jsonb, 48, 'a1b2c3d', 52, true, '2026-10-26T12:00:00Z', 'genesis'),
    ('0xDanomite/alloy-stellar', 'https://github.com/0xDanomite/alloy-stellar', 'Cross-chain liquidity router for Stellar Soroban', 9, '0xDanomite', NULL, NULL, NULL, 'main', NULL, 'TypeScript', 'Apache-2.0', 1, '2026-10-25T09:30:00Z', '2026-10-26T11:15:00Z', ARRAY['stellar', 'defi'], ARRAY['search'], '{"ecosystems": ["rust", "js"], "packages": {"soroban-sdk": "22.0.0", "@stellar/stellar-sdk": "13.0.0"}}'::jsonb, 64, 'b2c3d4e', 70, true, '2026-10-26T12:00:00Z', 'scale'),
    ('ygk94/4ward', 'https://github.com/ygk94/4ward', 'Forward pricing contracts and hedging on Soroban', 7, 'ygk94', NULL, NULL, NULL, 'main', 'https://fistea-hackmeridian.vercel.app', 'TypeScript', 'NOASSERTION', 1, '2026-10-25T11:49:37Z', '2026-10-26T11:45:00Z', ARRAY['soroban'], ARRAY['search'], '{"ecosystems": ["rust", "js"], "packages": {"soroban-sdk": null, "@stellar/stellar-sdk": "17.4.0", "@creit.tech/stellar-wallets-kit": "2.7.1"}}'::jsonb, 138, 'c3d4e5f', 140, true, '2026-10-26T12:00:00Z', 'genesis'),
    ('troqpay/private-yield', 'https://github.com/troqpay/private-yield', 'Privacy-preserving yield aggregator on Stellar', 6, 'troqpay', NULL, NULL, NULL, 'main', NULL, 'Rust', 'MIT', 0, '2026-10-25T10:05:00Z', '2026-10-26T10:50:00Z', ARRAY['stellar', 'privacy'], ARRAY['search'], '{"ecosystems": ["rust"], "packages": {"soroban-sdk": "22.0.0"}}'::jsonb, 35, 'd4e5f6a', 39, true, '2026-10-26T12:00:00Z', 'genesis'),
    ('hustle1hustle/bookerbob-hackmeridian-2026', 'https://github.com/hustle1hustle/bookerbob-hackmeridian-2026', 'On-chain orderbook and escrow settlement on Stellar', 5, 'hustle1hustle', NULL, NULL, NULL, 'main', NULL, 'TypeScript', 'MIT', 0, '2026-10-25T10:20:00Z', '2026-10-26T10:40:00Z', ARRAY['hackmeridian', 'stellar'], ARRAY['search'], '{"ecosystems": ["js"], "packages": {"@stellar/stellar-sdk": "13.0.0"}}'::jsonb, 29, 'e5f6a7b', 31, true, '2026-10-26T12:00:00Z', 'genesis'),
    ('enzoblain/ZKross', 'https://github.com/enzoblain/ZKross', 'Zero-knowledge bridge verifier for Soroban contracts', 8, 'enzoblain', NULL, NULL, NULL, 'main', NULL, 'Rust', 'MIT', 1, '2026-10-25T10:45:00Z', '2026-10-26T11:05:00Z', ARRAY['soroban', 'zk'], ARRAY['search'], '{"ecosystems": ["rust"], "packages": {"soroban-sdk": "22.0.0"}}'::jsonb, 41, 'f6a7b8c', 45, true, '2026-10-26T12:00:00Z', 'scale'),
    ('sample-org/stellar-split', 'https://github.com/sample-org/stellar-split', 'Instant bill splitting with Soroban smart accounts', 4, 'sample-org', NULL, NULL, NULL, 'main', NULL, 'TypeScript', 'MIT', 0, '2026-10-25T11:10:00Z', '2026-10-26T09:50:00Z', ARRAY['stellar'], ARRAY['search'], '{"ecosystems": ["js"], "packages": {"@stellar/stellar-sdk": "13.0.0"}}'::jsonb, 22, 'a7b8c9d', 25, true, '2026-10-26T12:00:00Z', 'genesis'),
    ('sample-org/meridian-pay', 'https://github.com/sample-org/meridian-pay', 'Streaming micropayments on Stellar testnet', 3, 'sample-org', NULL, NULL, NULL, 'main', NULL, 'Rust', 'MIT', 0, '2026-10-25T12:00:00Z', '2026-10-26T08:40:00Z', ARRAY['soroban'], ARRAY['search'], '{"ecosystems": ["rust"], "packages": {"soroban-sdk": "22.0.0"}}'::jsonb, 19, 'b8c9d0e', 20, true, '2026-10-26T12:00:00Z', 'genesis'),
    ('sample-org/soroban-escrow-kit', 'https://github.com/sample-org/soroban-escrow-kit', 'Composable milestone escrow templates for Stellar', 5, 'sample-org', NULL, NULL, NULL, 'main', NULL, 'TypeScript', 'Apache-2.0', 1, '2026-10-25T13:00:00Z', '2026-10-26T07:30:00Z', ARRAY['stellar', 'escrow'], ARRAY['search'], '{"ecosystems": ["js"], "packages": {"@stellar/stellar-sdk": "13.0.0"}}'::jsonb, 15, 'c9d0e1f', 18, true, '2026-10-26T12:00:00Z', 'genesis'),
    ('sample-org/anchor-pulse', 'https://github.com/sample-org/anchor-pulse', 'SEP-24 anchor telemetry and health monitor', 2, 'sample-org', NULL, NULL, NULL, 'main', NULL, 'Python', 'MIT', 0, '2026-10-25T14:00:00Z', '2026-10-26T06:20:00Z', ARRAY['stellar'], ARRAY['search'], '{"ecosystems": ["python"], "packages": {"stellar-sdk": "11.0.0"}}'::jsonb, 12, 'd0e1f2a', 14, true, '2026-10-26T12:00:00Z', 'scale')
ON CONFLICT (full_name) DO NOTHING;

INSERT INTO projects (
    project_id, full_name, footprint, tier, contracts, classic_ops, assets,
    wasm_uploads, failed_txs, builders, first_activity, last_activity
) VALUES
    ('repo:ethan-r13n/nest', 'ethan-r13n/nest', 'contracts', 'verified', 3, 12, 1, 2, 0, 1, '2026-10-25T09:20:00Z', '2026-10-26T11:10:00Z'),
    ('repo:0xDanomite/alloy-stellar', '0xDanomite/alloy-stellar', 'contracts', 'verified', 3, 8, 1, 2, 1, 1, '2026-10-25T10:15:00Z', '2026-10-26T10:45:00Z'),
    ('repo:ygk94/4ward', 'ygk94/4ward', 'contracts', 'verified', 3, 25, 2, 2, 0, 1, '2026-10-25T11:55:00Z', '2026-10-26T11:25:00Z'),
    ('repo:troqpay/private-yield', 'troqpay/private-yield', 'contracts', 'verified', 2, 4, 0, 1, 0, 1, '2026-10-25T13:10:00Z', '2026-10-26T09:15:00Z'),
    ('repo:hustle1hustle/bookerbob-hackmeridian-2026', 'hustle1hustle/bookerbob-hackmeridian-2026', 'contracts', 'verified', 2, 6, 1, 1, 0, 1, '2026-10-25T15:20:00Z', '2026-10-26T08:30:00Z'),
    ('repo:enzoblain/ZKross', 'enzoblain/ZKross', 'contracts', 'verified', 2, 3, 0, 1, 1, 1, '2026-10-25T17:05:00Z', '2026-10-26T07:45:00Z'),
    ('repo:sample-org/stellar-split', 'sample-org/stellar-split', 'contracts', 'verified', 2, 5, 0, 1, 0, 1, '2026-10-25T19:10:00Z', '2026-10-26T05:20:00Z'),
    ('repo:sample-org/meridian-pay', 'sample-org/meridian-pay', 'contracts', 'verified', 2, 2, 0, 1, 0, 1, '2026-10-25T21:30:00Z', '2026-10-26T03:15:00Z'),
    ('repo:sample-org/soroban-escrow-kit', 'sample-org/soroban-escrow-kit', 'contracts', 'likely', 1, 0, 0, 0, 0, 1, '2026-10-26T01:10:00Z', '2026-10-26T01:10:00Z'),
    ('repo:sample-org/anchor-pulse', 'sample-org/anchor-pulse', 'github', 'likely', 0, 0, 0, 0, 0, 0, NULL, NULL)
ON CONFLICT (project_id) DO NOTHING;

INSERT INTO contracts (
    contract_id, deployer, wasm_hash, tx_hash, ledger, deployed_at
) VALUES
    ('CSAMPLECONTRACT000000000000000000000000000000000000000001', 'GSAMPLEDEPLOYER0000000000000000000000000000000000000001', 'wasmhash01', 'txsample01', 100001, '2026-10-25T09:20:00Z'),
    ('CSAMPLECONTRACT000000000000000000000000000000000000000002', 'GSAMPLEDEPLOYER0000000000000000000000000000000000000002', 'wasmhash02', 'txsample02', 100002, '2026-10-25T10:15:00Z'),
    ('CSAMPLECONTRACT000000000000000000000000000000000000000003', 'GSAMPLEDEPLOYER0000000000000000000000000000000000000003', 'wasmhash03', 'txsample03', 100003, '2026-10-25T11:55:00Z'),
    ('CSAMPLECONTRACT000000000000000000000000000000000000000004', 'GSAMPLEDEPLOYER0000000000000000000000000000000000000001', 'wasmhash01', 'txsample04', 100004, '2026-10-25T12:30:00Z'),
    ('CSAMPLECONTRACT000000000000000000000000000000000000000005', 'GSAMPLEDEPLOYER0000000000000000000000000000000000000004', 'wasmhash04', 'txsample05', 100005, '2026-10-25T13:10:00Z'),
    ('CSAMPLECONTRACT000000000000000000000000000000000000000006', 'GSAMPLEDEPLOYER0000000000000000000000000000000000000002', 'wasmhash02', 'txsample06', 100006, '2026-10-25T14:25:00Z'),
    ('CSAMPLECONTRACT000000000000000000000000000000000000000007', 'GSAMPLEDEPLOYER0000000000000000000000000000000000000005', 'wasmhash05', 'txsample07', 100007, '2026-10-25T15:20:00Z'),
    ('CSAMPLECONTRACT000000000000000000000000000000000000000008', 'GSAMPLEDEPLOYER0000000000000000000000000000000000000003', 'wasmhash03', 'txsample08', 100008, '2026-10-25T16:40:00Z'),
    ('CSAMPLECONTRACT000000000000000000000000000000000000000009', 'GSAMPLEDEPLOYER0000000000000000000000000000000000000006', 'wasmhash06', 'txsample09', 100009, '2026-10-25T17:05:00Z'),
    ('CSAMPLECONTRACT000000000000000000000000000000000000000010', 'GSAMPLEDEPLOYER0000000000000000000000000000000000000007', 'wasmhash07', 'txsample10', 100010, '2026-10-25T19:10:00Z'),
    ('CSAMPLECONTRACT000000000000000000000000000000000000000011', 'GSAMPLEDEPLOYER0000000000000000000000000000000000000008', 'wasmhash08', 'txsample11', 100011, '2026-10-25T21:30:00Z'),
    ('CSAMPLECONTRACT000000000000000000000000000000000000000012', 'GSAMPLEDEPLOYER0000000000000000000000000000000000000009', 'wasmhash09', 'txsample12', 100012, '2026-10-26T01:10:00Z'),
    ('CSAMPLECONTRACT000000000000000000000000000000000000000013', 'GSAMPLEDEPLOYER0000000000000000000000000000000000000008', 'wasmhash08', 'txsample13', 100013, '2026-10-26T03:15:00Z'),
    ('CSAMPLECONTRACT000000000000000000000000000000000000000014', 'GSAMPLEDEPLOYER0000000000000000000000000000000000000007', 'wasmhash07', 'txsample14', 100014, '2026-10-26T05:20:00Z'),
    ('CSAMPLECONTRACT000000000000000000000000000000000000000015', 'GSAMPLEDEPLOYER0000000000000000000000000000000000000006', 'wasmhash06', 'txsample15', 100015, '2026-10-26T07:45:00Z'),
    ('CSAMPLECONTRACT000000000000000000000000000000000000000016', 'GSAMPLEDEPLOYER0000000000000000000000000000000000000005', 'wasmhash05', 'txsample16', 100016, '2026-10-26T08:30:00Z'),
    ('CSAMPLECONTRACT000000000000000000000000000000000000000017', 'GSAMPLEDEPLOYER0000000000000000000000000000000000000004', 'wasmhash04', 'txsample17', 100017, '2026-10-26T09:15:00Z'),
    ('CSAMPLECONTRACT000000000000000000000000000000000000000018', 'GSAMPLEDEPLOYER0000000000000000000000000000000000000002', 'wasmhash10', 'txsample18', 100018, '2026-10-26T10:45:00Z'),
    ('CSAMPLECONTRACT000000000000000000000000000000000000000019', 'GSAMPLEDEPLOYER0000000000000000000000000000000000000001', 'wasmhash11', 'txsample19', 100019, '2026-10-26T11:10:00Z'),
    ('CSAMPLECONTRACT000000000000000000000000000000000000000020', 'GSAMPLEDEPLOYER0000000000000000000000000000000000000003', 'wasmhash12', 'txsample20', 100020, '2026-10-26T11:25:00Z')
ON CONFLICT (contract_id) DO NOTHING;

INSERT INTO links (full_name, subject_kind, subject, method) VALUES
    ('ethan-r13n/nest', 'contract', 'CSAMPLECONTRACT000000000000000000000000000000000000000001', 'contract_in_repo'),
    ('ethan-r13n/nest', 'contract', 'CSAMPLECONTRACT000000000000000000000000000000000000000004', 'contract_in_repo'),
    ('ethan-r13n/nest', 'contract', 'CSAMPLECONTRACT000000000000000000000000000000000000000019', 'contract_in_repo'),
    ('0xDanomite/alloy-stellar', 'contract', 'CSAMPLECONTRACT000000000000000000000000000000000000000002', 'contract_in_repo'),
    ('0xDanomite/alloy-stellar', 'contract', 'CSAMPLECONTRACT000000000000000000000000000000000000000006', 'contract_in_repo'),
    ('0xDanomite/alloy-stellar', 'contract', 'CSAMPLECONTRACT000000000000000000000000000000000000000018', 'contract_in_repo'),
    ('ygk94/4ward', 'contract', 'CSAMPLECONTRACT000000000000000000000000000000000000000003', 'contract_in_repo'),
    ('ygk94/4ward', 'contract', 'CSAMPLECONTRACT000000000000000000000000000000000000000008', 'contract_in_repo'),
    ('ygk94/4ward', 'contract', 'CSAMPLECONTRACT000000000000000000000000000000000000000020', 'contract_in_repo'),
    ('troqpay/private-yield', 'contract', 'CSAMPLECONTRACT000000000000000000000000000000000000000005', 'contract_in_repo'),
    ('troqpay/private-yield', 'contract', 'CSAMPLECONTRACT000000000000000000000000000000000000000017', 'contract_in_repo'),
    ('hustle1hustle/bookerbob-hackmeridian-2026', 'contract', 'CSAMPLECONTRACT000000000000000000000000000000000000000007', 'contract_in_repo'),
    ('hustle1hustle/bookerbob-hackmeridian-2026', 'contract', 'CSAMPLECONTRACT000000000000000000000000000000000000000016', 'contract_in_repo'),
    ('enzoblain/ZKross', 'contract', 'CSAMPLECONTRACT000000000000000000000000000000000000000009', 'contract_in_repo'),
    ('enzoblain/ZKross', 'contract', 'CSAMPLECONTRACT000000000000000000000000000000000000000015', 'contract_in_repo'),
    ('sample-org/stellar-split', 'contract', 'CSAMPLECONTRACT000000000000000000000000000000000000000010', 'contract_in_repo'),
    ('sample-org/stellar-split', 'contract', 'CSAMPLECONTRACT000000000000000000000000000000000000000014', 'contract_in_repo'),
    ('sample-org/meridian-pay', 'contract', 'CSAMPLECONTRACT000000000000000000000000000000000000000011', 'contract_in_repo'),
    ('sample-org/meridian-pay', 'contract', 'CSAMPLECONTRACT000000000000000000000000000000000000000013', 'contract_in_repo'),
    ('sample-org/soroban-escrow-kit', 'contract', 'CSAMPLECONTRACT000000000000000000000000000000000000000012', 'deployer_in_repo')
ON CONFLICT (subject_kind, subject, full_name) DO NOTHING;

INSERT INTO repo_contributors (full_name, login, url, avatar_url, contributions) VALUES
    ('ethan-r13n/nest', 'ethan-r13n', 'https://github.com/ethan-r13n', NULL, 48),
    ('0xDanomite/alloy-stellar', '0xDanomite', 'https://github.com/0xDanomite', NULL, 64),
    ('ygk94/4ward', 'ygk94', 'https://github.com/ygk94', NULL, 96),
    ('troqpay/private-yield', 'troqpay', 'https://github.com/troqpay', NULL, 35),
    ('hustle1hustle/bookerbob-hackmeridian-2026', 'hustle1hustle', 'https://github.com/hustle1hustle', NULL, 29),
    ('enzoblain/ZKross', 'enzoblain', 'https://github.com/enzoblain', NULL, 41)
ON CONFLICT (full_name, login) DO NOTHING;
