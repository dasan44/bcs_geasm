####################################################################################
##
## Name         : scanner_materiel_geasm.py
## Author       : David Sanagustin
## Version init : 1.0
## Date         : 05/2020
## Plateform    : Windows / Linux 
## Depot git    : https://github.com/dasan44/bcs_geasm.git
##
##
## Pre-req      : MySQL server 
##                python 2.7 (minimum), fonctionne sur python 3.7
##                pip install mysql-connector-python
##                pip install cryptography
##                fichier mysql.bin contient le mot de passe de la base
##
####################################################################################
## 
## Scanner de code barre permettant le suivi et la gestion du materiel du club
## de plongee G.E.A.S.M. : https://www.geasm.org
##
## Emprunter un / des gilet(s) stabilisateur, un / des detendeur(s), 
## une / des bouteille(s) / autre materiel appartenant au G.E.A.S.M.
## 
## Pour chaque emprunt de materiel il faut scanner sa carte de membre avant !
## 1) scanner sa carte de membre
## 2) scanner un materiel
## 3) scanner sa carte de membre
## 4) scanner un autre materiel (si le meme materiel est rescanné il est alors mis 
##    a jour (revient en stock et repart)
## 
## Pour remettre du materiel en stock il suffit de scanner le materiel sorti
## pas besoin de carte membre pour rentrer le materiel
##
## Le materiel et les membres doivent etre connus et enregistres en base !
##
####################################################################################

# Reste à faire LOG DES ERREURS !
# Script backup MYSQL + tgz + cron
# Script cherche wifi/connection internet + upload bakcup mysql vers geasm.org
# Print des actions
# enregistrer les codes barre non trouves en base (fichier inconnus.log)

import time
import sys
import select
import os
from os import path
from datetime import date, datetime, timedelta
import mysql.connector

ficBinMysql='fichiersortie.bin'
action='scan'
id_memb='aucun'

def interruptProg():
    #print ("Fermeture de l'application")
    exit()

def connexionDB():
    # fonction de connexion a la base de donnee
    global mydb
    global mycursor
    from cryptography.fernet import Fernet
    key = b'No6-nO0fCXeVfXpt9u58UO9Z05EZMEAwqIvqWZxadto='
    cipher_suite = Fernet(key)
    with open(ficBinMysql, 'rb') as file_object:
        for line in file_object:
            encryptedpwd = line
    uncipher_text = (cipher_suite.decrypt(encryptedpwd))
    dcodedb = bytes(uncipher_text).decode("utf-8")
    addrhost, usrbdd, pwdbdd, dbname = dcodedb.split(';')
    try:
        mydb = mysql.connector.connect(
         host=addrhost,
         user=usrbdd,
         passwd=pwdbdd,
         database=dbname,
         auth_plugin='mysql_native_password')
        mycursor = mydb.cursor()
    except mysql.connector.Error as err:
        #print("Erreur de connexion a la base mysql du GEASM: {}".format(err))
        interruptProg()

# traitement retour du materiel
def retour_materiel(id_materiel, id_mvt):
    # fonction retour du materiel
    global mydb
    global mycursor
    try:
        connexionDB()
        mycursor.execute("UPDATE materiels SET statut = 'in', id_mvt = '' WHERE id_materiel = '%s'" % id_materiel)
        mycursor.fetchone()
        mydb.commit()
	    #on verifie que la requete select n'affiche rien sinon erreur
        #mycursor.execute("SELECT id_materiel FROM materiels where id_materiel = '%s' and statut = 'out'" % id_materiel)
        #myresult = mycursor.fetchall()
        #rc = mycursor.rowcount
	    #print("nombre de ligne: "%rc)
        #if rc == 1:
        #    print("ERREUR UPDATE MATERIEL !")
        #else:
        #    print("UPDATE OK")
        dateretourcalc = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        mycursor.execute("UPDATE mvts_materiels SET date_retour = '%s' where id_mvt = '%s'" % (dateretourcalc,id_mvt))
        mycursor.fetchone()
        mydb.commit()
        #mycursor.execute("SELECT date_retour FROM mvts_materiels where id_mvt = '%s'" % id_mvt)
        #myresult = mycursor.fetchall()
        #rc = mycursor.rowcount
        mycursor.close()
        mydb.close()
        #if rc == 1:
        #    print("UPDATE OK")
        #else:
        #    print("ERREUR UPDATE MVT!!!")
    except mysql.connector.Error as err:
        #print("Erreur de connexion a la base mysql du GEASM: {}".format(err))
        interruptProg()
	#mettre a jour la table materiel (statut = in au lieu de out)
    #mettre a our la table mvt (date retour ...)
    #retour au mode scan initial

def scan_windows():
    # fonction scanner sur os windows
    # fonction de base qui tourne en boucle pour scanner les codes barres
    global action
    global id_memb
    global mydb
    global mycursor
    import msvcrt
    try:
        while True:
            if msvcrt.kbhit():
                if action == 'emprunt':
                    # ajout une entree dans la table mvts_materiels
                    # update table materiel ==> materiel = out
                    # reset de la variable action pour le prochain scan
                    action = 'scan'
                    key_stroke = list(input(msvcrt.getch().decode('ascii')).split())
                    # suppression de caracteres inutils, probleme lies a windows
                    # un code barre 123456 sera lu et affiche comme suit ['23456']
                    # le premier caracetere n'est pas interprete
                    # suppression des crochets et des '
                    # resultat code barre = 23456
                    varToSearch = str(key_stroke).replace('[', '').replace(']','').replace('\'', '')
                    # verifier que le materiel existe dans la base
                    connexionDB()
                    try:
                        mycursor.execute("SELECT id_materiel FROM materiels where id_materiel = '%s'" % varToSearch)
                        myresult = mycursor.fetchall()
                        rc = mycursor.rowcount
                        mycursor.close()
                        mydb.close()
                        if rc == 1:
                            # le materiel existe en base on peut l'emprunter
                            # sinon  / else on ne fait rien !
                            # verification si le materiel n'est pas deja sorti
                            # si jamais oubli de scan retour
                            check_if_out(varToSearch)
                            connexionDB()
                            mycursor.execute("SELECT id_mvt FROM mvts_materiels ORDER BY id_mvt DESC LIMIT 1")
                            myresult = mycursor.fetchall()
                            rc = mycursor.rowcount
                            mycursor.close()
                            mydb.close()
                            for row in myresult:
                                # incrementation pour table mouvement
                                id_mvt_calc = int(row[0])+1
                            dateretourcalc = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            requete_base("INSERT INTO mvts_materiels (id_mvt,id_materiel,id_membre,date_emprunt) VALUES ('%s','%s','%s','%s')" % (id_mvt_calc,varToSearch,id_memb,dateretourcalc), 'insert', id_mvt_calc)
					        # mise a jour table materiel
                            requete_base("UPDATE materiels SET statut = 'out', id_mvt = '%s' WHERE id_materiel = '%s'" % (id_mvt_calc,varToSearch), 'update', varToSearch)
                    except mysql.connector.Error as err:
                        #print("Erreur de connexion a la base mysql du GEASM: {}".format(err))
                        interruptProg()
                else:
                    # premier scan
					# suppression de caracteres inutils, probleme lies a windows
                    # un code barre 123456 sera lu et affiche comme suit ['23456']
                    # le premier caracetere n'est pas interprete
                    # suppression des crochets et des '
                    # resultat code barre = 23456
                    key_stroke = list(input(msvcrt.getch().decode('ascii')).split())
                    varToSearch = str(key_stroke).replace('[', '').replace(']','').replace('\'', '')
                    requete_base("SELECT id_membre FROM membres where id_membre = '" + str(varToSearch) + "'", 'membre', varToSearch)
    except KeyboardInterrupt:
        interruptProg()

def scan_linux():
    # fonction scanner sur os linux
    # fonction de base qui tourne en boucle pour scanner les codes barres
    global action
    global id_memb
    global mydb
    global mycursor
    stdin_fd = sys.stdin.fileno()
    try:
        while True:
            if action == 'emprunt':
                # ajout une entree dans la table mvts_materiels
                # update table materiel ==> materiel = out
                # reset de la variable action pour le prochain scan
                action = 'scan'
                sys.stdout.flush()
                r_list = [stdin_fd]
                w_list = list()
                x_list = list()
                r_list, w_list, x_list = select.select(r_list, w_list, x_list)
                if stdin_fd in r_list:
                    result = os.read(stdin_fd, 1024)
                    result = result.rstrip()
                    result = [line.rstrip() for line in result.split('\n')]
                    for line in result:
                        # verifier que le materiel existe dans la base
                        varToSearch = line
                    connexionDB()
                    try:
                        mycursor.execute("SELECT id_materiel FROM materiels where id_materiel = '%s'" % varToSearch)
                        myresult = mycursor.fetchall()
                        rc = mycursor.rowcount
                        mycursor.close()
                        mydb.close()
                        if rc == 1:
                            # le materiel existe en base on peut l'emprunter
                            # sinon  / else on ne fait rien !
                            # verification si le materiel n'est pas deja sorti
                            # si jamais oubli de scan retour
                            check_if_out(varToSearch)
                            connexionDB()
                            mycursor.execute("SELECT id_mvt FROM mvts_materiels ORDER BY id_mvt DESC LIMIT 1")
                            myresult = mycursor.fetchall()
                            rc = mycursor.rowcount
                            mycursor.close()
                            mydb.close()
                            
                            for row in myresult:
                                # incrementation pour table mouvement
                                id_mvt_calc = int(row[0])+1
                            dateretourcalc = datetime.now().strftime("%Y-%m-%d %H:%M:%S")                            
                            requete_base("INSERT INTO mvts_materiels (id_mvt,id_materiel,id_membre,date_emprunt) VALUES ('%s','%s','%s','%s')" % (id_mvt_calc,varToSearch,id_memb,dateretourcalc), 'insert', id_mvt_calc)
					        # mise a jour table materiel
                            requete_base("UPDATE materiels SET statut = 'out', id_mvt = '%s' WHERE id_materiel = '%s'" % (id_mvt_calc,varToSearch), 'update', varToSearch)
                    except mysql.connector.Error as err:
                            #print("Erreur de connexion a la base mysql du GEASM: {}".format(err))
                            interruptProg()
            else:
                # premier scan
                sys.stdout.flush()
                r_list = [stdin_fd]
                w_list = list()
                x_list = list()
                r_list, w_list, x_list = select.select(r_list, w_list, x_list)
                if stdin_fd in r_list:
                    result = os.read(stdin_fd, 1024)
                    result = result.rstrip()
                    result = [line.rstrip() for line in result.split('\n')]
                    for line in result:
                        requete_base("SELECT id_membre FROM membres where id_membre = '%s'" % line, 'membre', line)
    except KeyboardInterrupt:
        interruptProg()

def test_db():
    # procedure de verification connectivite a la base mysql
    # au lancement du programme
    global mydb
    global mycursor
    connexionDB()
    mydb.close()

def check_if_out(id_materiel):
    # procedure de verification si le materiel est OUT
    # si out ==> on le rentre
    global mydb
    global mycursor
    #print("check_if_out")
	# verification de l'etat du materiel
    try:
        connexionDB()
        mycursor.execute("SELECT id_mvt FROM materiels where id_materiel = '%s' and statut = 'out'" % id_materiel)
        myresult = mycursor.fetchall()
        rc = mycursor.rowcount
        mycursor.close()
        mydb.close()
		#print("nombre de ligne: "%rc)
        if rc == 1:
            #print("materiel a retourner !")
            for row in myresult:
                #print("id_mvt :", row[0])
                id_mvt = row[0]
            # Materiel identifie comme sorti donc on le rentre (modification de table mvt et materiel)
            retour_materiel(id_materiel, id_mvt)
    except mysql.connector.Error as err:
        #print("Erreur de connexion a la base mysql du GEASM: {}".format(err))
        interruptProg()

def requete_base(req, type, id):
    # procedure generique d'execution de requetes
    global id_memb
    global action
    global mydb
    global mycursor
    try:    
        if type == 'insert':
            connexionDB()
            mycursor.execute(req)
            mycursor.fetchone()
            mydb.commit()
            mycursor.close()
            mydb.close()
        elif type == 'update':
            connexionDB()
            mycursor.execute(req)
            mycursor.fetchone()
            mydb.commit()
            mycursor.close()
            mydb.close()
        else:
            connexionDB()
            mycursor.execute(req)
            myresult = mycursor.fetchall()
            rc = mycursor.rowcount
            mycursor.close()
            mydb.close()
            if rc == 1:
                if type == 'membre':
                    for row in myresult:
                        id_memb = row[0]
                        action = 'emprunt'
                if type == 'materiel':
                    #print("appel fonction is_out")
			        # on verifie si il est sorti
                    check_if_out(id)   
                # Materiel identifie comme sorti donc on le rentre (modification de table mvt et materiel)
                #retour_materiel(varToSearch)
            else:
                #print("rc = 0")
                # on verifie si il ne s'agit pas de materiel qui serait sorti et qui va rentrer
                check_if_out(id) 
    except mysql.connector.Error as err:
        #print("Erreur de connexion a la base mysql du GEASM: {}".format(err))
        interruptProg()

def main():
    # Main - Debut du programme
    # controle presence fichier .bin pour mysql
    if not path.exists(ficBinMysql):
        #print("Erreur fichier " + ficBinMysql + " manquant !")
        interruptProg()
    # mysql
    # test de connexion a la base
    test_db()
    # controle OS
    # Si plateforme windows
    if sys.platform.startswith('win'):
        scan_windows()
    else:
        scan_liux()

# Debut appel de main
main()