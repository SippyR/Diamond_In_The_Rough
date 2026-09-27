DROP TABLE IF EXISTS player_stats;

CREATE TABLE player_stats (
    fangraphs_player_id VARCHAR(50),
    bbref_player_id VARCHAR(50),
    season INT,
    name_ascii VARCHAR(100),
    primary_position VARCHAR(10),
    g INT, pa INT, ab INT, r INT, h INT, 
    "1b" INT, "2b" INT, "3b" INT, hr INT, rbi INT, 
    sb INT, cs INT, bb INT, so INT, ibb INT, 
    hbp INT, sf INT, sh INT, gdp INT, 
    "wRC+" FLOAT, "era-" FLOAT, w INT, l INT, 
    "g.1" INT, gs INT, cg INT, sho INT, sv INT, 
    era FLOAT, ip FLOAT, "h.1" INT, er INT, 
    "r.1" INT, "hr.1" INT, "bb.1" INT, "so.1" INT, 
    "ibb.1" INT, whip FLOAT, wp INT, "hbp.1" INT, 
    bk INT, tbf INT, war FLOAT,
    team VARCHAR(50) -- Moved to the very end
);