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
INSERT INTO `geasm`.`membres`(id_membre,nom,pnom,niveau,droits,date_ajout) VALUES ('21-00260000223001885','uuuu','ppppp','n3','admin','2020-05-17 00:00:00');

