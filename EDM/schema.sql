-- PostgreSQL
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS user_roles CASCADE;
DROP TABLE IF EXISTS utd_documents CASCADE;
DROP TABLE IF EXISTS contract_documents CASCADE;
DROP TABLE IF EXISTS document_statuses CASCADE;
DROP TABLE IF EXISTS document_types CASCADE;
DROP TABLE IF EXISTS counterparties CASCADE;
DROP TABLE IF EXISTS utd_document_items CASCADE;
DROP TABLE IF EXISTS register_requests CASCADE;

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
    role INTEGER DEFAULT NULL,
    has_signature BOOLEAN NOT NULL DEFAULT FALSE,
    add_employee BOOLEAN NOT NULL DEFAULT FALSE,
    organization INTEGER DEFAULT NULL,
    blocked BOOLEAN NOT NULL DEFAULT FALSE,
    login VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(80) NOT NULL,
    send_tin BOOLEAN NOT NULL DEFAULT FALSE, -- Для проверки почсле регистрации
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
    number VARCHAR(255) NOT NULL UNIQUE, -- Номер
    counterparty INTEGER NOT NULL, -- Получатель документа
    creator INTEGER NOT NULL, -- Создатель
    creator_counterparty INTEGER NOT NULL, -- Отправитель
    consignee INTEGER NOT NULL, -- Грузополучатель
    provider INTEGER NOT NULL, -- Поставщик
    payer INTEGER NOT NULL, -- Плательщк
    amount DECIMAL(15, 2), -- Сумма
    document_type INTEGER NOT NULL, -- Тип документа
    document_status INTEGER NOT NULL, -- Статус
    sender_signature INTEGER DEFAULT NULL, -- Подпись отправителя
    recipient_signature INTEGER DEFAULT NULL, -- Подпись получателя
    date_of_receipt DATE DEFAULT NULL, -- Дата получения
    file_path TEXT DEFAULT NULL, -- Путь к файлу
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

CREATE TABLE utd_document_items (
    id SERIAL PRIMARY KEY,
    utd_document_id INTEGER NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    product_quantity INTEGER NOT NULL,
    product_price DECIMAL(100, 2) NOT NULL,
    product_sum DECIMAL(100, 2) NOT NULL,
    FOREIGN KEY (utd_document_id) REFERENCES utd_documents(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE INDEX idx_utd_document_items_utd_document_id ON utd_document_items(utd_document_id);

-- Договора / Контракты
CREATE TABLE contract_documents (
    id SERIAL PRIMARY KEY,
    number VARCHAR(255) NOT NULL UNIQUE,
    counterparty INTEGER NOT NULL, -- Получатель документа
    creator INTEGER NOT NULL,
    creator_counterparty INTEGER NOT NULL,
    document_type INTEGER NOT NULL, -- Тип документа
    document_status INTEGER NOT NULL, -- Статус
    provider INTEGER NOT NULL, -- поставщик
    provider_base TEXT NOT NULL, -- основание поставщика
    client INTEGER NOT NULL, -- заказщик
    client_base TEXT NOT NULL, -- основание заказщика
    address VARCHAR(255) NOT NULL, -- адрес получателя
    text TEXT DEFAULT NULL, -- текст договора
    provider_signature INTEGER DEFAULT NULL,
    client_signature INTEGER DEFAULT NULL,
    date_of_receipt DATE DEFAULT NULL, -- Дата получения
    file_path TEXT DEFAULT NULL, -- Путь к файлу
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE,
    FOREIGN KEY (creator) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (creator_counterparty) REFERENCES counterparties(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (provider) REFERENCES counterparties(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (client) REFERENCES counterparties(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (provider_signature) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (client_signature) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE register_requests (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    tin VARCHAR(12) NOT NULL,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE INDEX idx_users_id ON users(id);
CREATE INDEX idx_utd_documents_number ON utd_documents(number);
CREATE INDEX idx_contract_documents_number ON contract_documents(number);
