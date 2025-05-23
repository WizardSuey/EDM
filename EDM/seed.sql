INSERT INTO user_roles (name, description)
VALUES ('admin', 'Роль администратора предназначена для пользователей, которые имеют полный доступ к системе. Администраторы могут управлять учетными записями пользователей, настраивать настройки системы и контролировать все операции в приложении. Эта роль обычно назначается доверенному персоналу, который несет ответственность за поддержание целостности и безопасности системы.');

INSERT INTO document_types (name, description)
VALUES 
('УПД', 'Универсальный передаточный документ (УПД)'),
('Договор', 'Документ договора');

INSERT INTO document_statuses (name, description)
VALUES
('Создан', 'Документ только что создан, не подписан и не отправлен контрагенту'),
('Отправлен', 'Документ отправлен контрагенту и ожидает подтверждения получения.'),
('Получен', 'Контрагент подтвердил получение документа.'),
('На подписи', 'Документ ожидает подписи от одной или нескольких сторон.'),
('Подписан', 'Документ подписан всеми необходимыми сторонами.'),
('Согласован', 'Документ согласован всеми необходимыми сторонами.'),
('Отклонён', 'Документ отклонён одной из сторон, возможно, с указанием причин.'),
('Архивирован', 'Документ завершил свой жизненный цикл и перемещён в архив для хранения.');

INSERT INTO counterparties (name, tin, email, phone_number, address, created_at, updated_at)
VALUES 
('UniversamBand', '0000000000', 'dorogino@gmail.com', '86666666666', 'Луна 6 бизнес колония', NOW(), NOW()),
('TechCorp', '1111111111', 'techcorp@example.com', '80000000001', '123 Tech Street', NOW(), NOW()),
('GreenEnergy', '2222222222', 'greenenergy@example.com', '80000000002', '456 Solar Ave', NOW(), NOW()),
('Foodies', '3333333333', 'foodies@example.com', '80000000003', '789 Culinary Blvd', NOW(), NOW()),
('HealthPlus', '4444444444', 'healthplus@example.com', '80000000004', '101 Wellness Way', NOW(), NOW()),
('EduWorld', '5555555555', 'eduworld@example.com', '80000000005', '202 Learning Lane', NOW(), NOW()),
('AutoDrive', '6666666666', 'autodrive@example.com', '80000000006', '303 Motorway', NOW(), NOW()),
('FashionHub', '7777777777', 'fashionhub@example.com', '80000000007', '404 Style St', NOW(), NOW()),
('AquaLife', '8888888888', 'aqualife@example.com', '80000000008', '505 Ocean Drive', NOW(), NOW()),
('BuildIt', '9999999999', 'buildit@example.com', '80000000009', '606 Construct Ct', NOW(), NOW()),
('TravelSphere', '1010101010', 'travelsphere@example.com', '80000000010', '707 Journey Rd', NOW(), NOW());

INSERT INTO users (name, second_name, surname, date_of_birth, role, has_signature, add_employee, organization, blocked, login, email, password_digest, created_at, updated_at)
VALUES ('Flea', 'None', 'None', '1765-12-12', 1, TRUE, TRUE, 1, FALSE, 'admin', 'dorogino@gmail.com', 'scrypt:32768:8:1$VrAjHvnSWYpBVXio$c5cba30b97a7fa8addfc1dc9865119b4eaed98c68f2e9b9c573733d3e24256258cab222fefac2fa6ddf4b549281a8ca24f85f7166b25a79d46be6e3efb1e8363', NOW(), NOW());