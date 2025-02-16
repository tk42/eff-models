-- +goose Up
-- +goose StatementBegin

-- 市場
CREATE TABLE IF NOT EXISTS markets (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    name     TEXT    NOT NULL,
    address  TEXT
);

-- 市況
CREATE TABLE IF NOT EXISTS market_conditions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    market_id       INTEGER NOT NULL,
    round           INTEGER NOT NULL,
    date            TEXT    NOT NULL,   -- SQLite では日付は TEXT などで管理する
    shipped_volume  REAL    NOT NULL,   -- 出荷材積
    FOREIGN KEY (market_id) REFERENCES markets (id)
);

-- 樹種
CREATE TABLE IF NOT EXISTS tree_species (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT    NOT NULL
);

-- 径級
CREATE TABLE IF NOT EXISTS diameter_classes (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT    NOT NULL
);

-- 価格
CREATE TABLE IF NOT EXISTS prices (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    market_condition_id INTEGER NOT NULL,
    tree_species_id     INTEGER NOT NULL,
    diameter_class_id   INTEGER,        -- NULL を許容
    length              REAL    NOT NULL,  -- 長さ
    top_diameter_min    REAL    NOT NULL,  -- 末口径_最小
    top_diameter_max    REAL    NOT NULL,  -- 末口径_最大
    price_low           REAL    NOT NULL,  -- 価格安値
    price_middle        REAL,           -- 価格仲値, NULL を許容
    price_high          REAL    NOT NULL,  -- 価格高値
    tone                TEXT,           -- 気配, NULL を許容
    summary             TEXT,           -- 摘要, NULL を許容
    FOREIGN KEY (market_condition_id) REFERENCES market_conditions (id),
    FOREIGN KEY (tree_species_id)       REFERENCES tree_species (id),
    FOREIGN KEY (diameter_class_id)     REFERENCES diameter_classes (id)
);

-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin

DROP TABLE IF EXISTS prices;
DROP TABLE IF EXISTS diameter_classes;
DROP TABLE IF EXISTS tree_species;
DROP TABLE IF EXISTS market_conditions;
DROP TABLE IF EXISTS markets;

-- +goose StatementEnd
