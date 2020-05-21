################################
# INIT - Schema et tables GEASM
################################

#########
# Schema
#########
CREATE SCHEMA IF NOT EXISTS geasm;

#########
# Tables
#########
CREATE TABLE `geasm`.`mvts_materiels` (
  `id_mvt` VARCHAR(128) NOT NULL,
  `id_materiel` VARCHAR(128) NOT NULL,
  `id_membre` VARCHAR(128) NOT NULL,
  `date_emprunt` DATETIME NOT NULL,
  `date_retour` DATETIME,
  PRIMARY KEY (`id_mvt`))
ENGINE = InnoDB
COMMENT = 'Table de gestion des mouvements du materiel';

CREATE TABLE `geasm`.`materiels` (
  `id_materiel` VARCHAR(128) NOT NULL,
  `type` VARCHAR(128) NOT NULL,
  `caracteristiques` VARCHAR(128) NOT NULL,
  `date_ajout` DATETIME NOT NULL,
  `date_achat` DATETIME NOT NULL,
  `statut` VARCHAR(128) NOT NULL,
  `id_mvt` VARCHAR(128),
  PRIMARY KEY (`id_materiel`))
ENGINE = InnoDB
COMMENT = 'Table de gestion des materiels';

CREATE TABLE `geasm`.`membres` (
  `id_membre` VARCHAR(128) NOT NULL,
  `nom` VARCHAR(128) NOT NULL,
  `pnom` VARCHAR(128) NOT NULL,
  `niveau` VARCHAR(128),
  `droits` VARCHAR(128) NOT NULL,
  `date_ajout` DATETIME NOT NULL,
  PRIMARY KEY (`id_membre`))
ENGINE = InnoDB
COMMENT = 'Table de gestion des membres';

###############################################################
# Init data table mvts_materiels
# permet d'obtenir un numero id_mvt pour le prochain emprunt
###############################################################
INSERT INTO `geasm`.`mvt_materiels`(id_mvt,id_materiel,id_membre,date_emprunt,date_retour) VALUES ('1111111111','INIT','INIT','2020-05-01 00:00:00','2020-05-01 00:00:00');


###############################################################
# Donnees de tests
###############################################################

###############################################################
# Init data table materiels
###############################################################
INSERT INTO `geasm`.`materiels`(id_materiel,type,caracteristiques,date_ajout,date_achat,statut,id_mvt) VALUES ('A001-00260000223001885','bouteille','12l','2020-05-17 00:00:00','2014-12-01 00:00:005','out','1111111111');
INSERT INTO `geasm`.`materiels`(id_materiel,type,caracteristiques,date_ajout,date_achat,statut,id_mvt) VALUES ('111111','stab','L','2020-05-17 00:00:00','2014-12-01 00:00:00','in','');
INSERT INTO `geasm`.`materiels`(id_materiel,type,caracteristiques,date_ajout,date_achat,statut,id_mvt) VALUES ('222222','stab','M','2020-05-17 00:00:00','2014-12-01 00:00:00','in','');
INSERT INTO `geasm`.`materiels`(id_materiel,type,caracteristiques,date_ajout,date_achat,statut,id_mvt) VALUES ('444444','detendeur','L','2020-05-17 00:00:00','2014-12-01 00:00:00','in','');
INSERT INTO `geasm`.`materiels`(id_materiel,type,caracteristiques,date_ajout,date_achat,statut,id_mvt) VALUES ('21237/00302479','bouteille','12l','2020-05-17 00:00:00','2014-12-01 00:00:005','in','');
INSERT INTO `geasm`.`materiels`(id_materiel,type,caracteristiques,date_ajout,date_achat,statut,id_mvt) VALUES ('0A001-00260000223001885','bouteille','12l','2020-05-17 00:00:00','2014-12-01 00:00:005','in','');

###############################################################
# Init data table membres
###############################################################
INSERT INTO `geasm`.`membres`(id_membre,nom,pnom,niveau,droits,date_ajout) VALUES ('user1','nom1','pnom1','n1','membre','2020-05-17 00:00:00');
INSERT INTO `geasm`.`membres`(id_membre,nom,pnom,niveau,droits,date_ajout) VALUES ('user2','nom2','pnom2','n1','membre','2020-05-17 00:00:00');
INSERT INTO `geasm`.`membres`(id_membre,nom,pnom,niveau,droits,date_ajout) VALUES ('user3','nom3','pnom3','n2','membre','2020-05-17 00:00:00');
INSERT INTO `geasm`.`membres`(id_membre,nom,pnom,niveau,droits,date_ajout) VALUES ('user4','nom4','pnom4','n2','admin','2020-05-17 00:00:00');
INSERT INTO `geasm`.`membres`(id_membre,nom,pnom,niveau,droits,date_ajout) VALUES ('user5','nom5','pnom5','n3','membre','2020-05-17 00:00:00');
INSERT INTO `geasm`.`membres`(id_membre,nom,pnom,niveau,droits,date_ajout) VALUES ('user6','nom6','pnom6','n4','membre','2020-05-17 00:00:00');
INSERT INTO `geasm`.`membres`(id_membre,nom,pnom,niveau,droits,date_ajout) VALUES ('21-00260000223001885','sanagu','david','n3','admin','2020-05-17 00:00:00');


# 1) scanner le materiel pour le rentrer automatiquement
# verifier les bases
SELECT * FROM `geasm`.`mvts_materiels` where id_mvt = '122222228' and id_materiel = 'A001-00260000223001885';
# doit faire 0 ligne
SELECT * FROM `geasm`.`materiels` where id_materiel = 'A001-00260000223001885' and statut = 'out';
# doit faire 0 ligne
# 2) puis jouer les scenarios 
## scenario test materiel sorti à scanner pour simuler un retour
#  recupere un id, faire +1
SELECT id_mvt FROM `geasm`.`mvts_materiels` ORDER BY id_mvt DESC LIMIT 1;
# faire +1 sur l'id et le mettre dans id_mvt
UPDATE `geasm`.`materiels` SET statut = 'out', id_mvt = '122222228' WHERE id_materiel = 'A001-00260000223001885';
INSERT INTO `geasm`.`mvts_materiels` (id_mvt,id_materiel,id_membre,date_emprunt) VALUES ('122222228','A001-00260000223001885','KU324796-gE;!P','2020-05-19 23:35:04')
## scenario test materiel present, scanner une carte utilisateur et 1 materiel pour le sortir
UPDATE `geasm`.`materiels` SET statut = 'in', id_mvt = '' WHERE id_materiel = 'A001-00260000223001885';
UPDATE `geasm`.`materiels` SET date_retour = '2020-05-19 23:35:04' where id_mvt = '122222228'
# 3) scanner une carte membre
# 4) scanner un materiel
# verifier les bases
SELECT * FROM `geasm`.`mvts_materiels` where id_mvt = '122222228' and id_materiel = 'A001-00260000223001885';
# doit faire 1 ligne
SELECT * FROM `geasm`.`materiels` where id_materiel = 'A001-00260000223001885' and statut = 'out';
# doit faire 1 ligne