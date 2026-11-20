ALTER TABLE integration_contracts DROP CONSTRAINT integration_contracts_pkey;

ALTER TABLE integration_contracts
ADD CONSTRAINT integration_contracts_pkey PRIMARY KEY (partner, network, contract_id);
