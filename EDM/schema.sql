-- PostgreSQL
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS user_roles CASCADE;
DROP TABLE IF EXISTS utd_documents CASCADE;
DROP TABLE IF EXISTS contract_documents CASCADE;
DROP TABLE IF EXISTS document_statuses CASCADE;
DROP TABLE IF EXISTS document_types CASCADE;
DROP TABLE IF EXISTS counterparties CASCADE;

CREATE TABLE user_roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE counterparties (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    tin VARCHAR(12) NOT NULL UNIQUE, -- ИНН
    email VARCHAR(80) NOT NULL,
    phone_number VARCHAR(15) NOT NULL UNIQUE, -- Adjusted for potential international numbers
    address VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    second_name VARCHAR(100),
    surname VARCHAR(100),
    date_of_birth DATE, -- Renamed for consistency
    role INTEGER NOT NULL,
    has_signature BOOLEAN NOT NULL DEFAULT FALSE,
    add_employee BOOLEAN NOT NULL DEFAULT FALSE,
    organization INTEGER NOT NULL,
    blocked BOOLEAN NOT NULL DEFAULT FALSE,
    login VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(80) NOT NULL,
    password_digest VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE,
    FOREIGN KEY (role) REFERENCES user_roles(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (organization) REFERENCES counterparties(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE document_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE document_statuses (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT
);

-- УПД
CREATE TABLE utd_documents (
    id SERIAL PRIMARY KEY,
    number VARCHAR(255) NOT NULL,
    creator INTEGER NOT NULL,
    creator_counterparty INTEGER NOT NULL,
    consignee INTEGER NOT NULL, -- Грузополучатель
    provider INTEGER NOT NULL, -- Поставщик
    payer INTEGER NOT NULL, -- Плательщк
    amount DECIMAL(15, 2), -- Changed to DECIMAL for monetary values
    document_type INTEGER NOT NULL,
    document_status INTEGER NOT NULL,
    sender_signature INTEGER NOT NULL,
    recipient_signature INTEGER NOT NULL,
    date_of_receipt DATE NOT NULL,
    file_path TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE,
    FOREIGN KEY (creator) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (creator_counterparty) REFERENCES counterparties(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (consignee) REFERENCES counterparties(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (provider) REFERENCES counterparties(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (payer) REFERENCES counterparties(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (document_type) REFERENCES document_types(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (document_status) REFERENCES document_statuses(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (sender_signature) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (recipient_signature) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Договора / Контракты
CREATE TABLE contract_documents (
    id SERIAL PRIMARY KEY,
    number VARCHAR(255) NOT NULL,
    creator INTEGER NOT NULL,
    creator_counterparty INTEGER NOT NULL,
    provider INTEGER NOT NULL, -- поставщик
    provider_base TEXT NOT NULL, -- основание поставщика
    client INTEGER NOT NULL, -- заказщик
    client_base TEXT NOT NULL, -- основание заказщика
    address VARCHAR(255) NOT NULL,
    provider_signature INTEGER NOT NULL,
    client_signature INTEGER NOT NULL,
    FOREIGN KEY (creator) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (creator_counterparty) REFERENCES counterparties(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (provider) REFERENCES counterparties(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (client) REFERENCES counterparties(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (provider_signature) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (client_signature) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Indexes for frequently queried columns
CREATE INDEX idx_users_id ON users(id);
CREATE INDEX idx_utd_documents_number ON utd_documents(number);
CREATE INDEX idx_contract_documents_number ON contract_documents(number);
