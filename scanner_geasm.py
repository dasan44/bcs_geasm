####################################################################################
##
## Name         : scanner_geasm.py
## Author       : David Sanagustin
## Version      : 1.3
## Date         : 05/2020
## Plateform    : Windows / Linux 
## Depot git    : https://github.com/dasan44/bcs_geasm.git
##
##
## Pre-req      : La solution complete est destinee à tourner sur Raspbery PI 3
##                tests sur : Raspbian kernel 4.19 - 2020-02-13-raspbian-buster.img
##                - MySQL server 
##                - python 2.7 (minimum), fonctionne sur python 3.7
##                - apt-get install python-smbus i2c-tools
##                - pip install mysql-connector-python
##                - pip install cryptography
##                - fichier mysql.bin
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
##   1) scanner sa carte de membre
##   2) scanner un materiel
##   3) scanner sa carte de membre
##   4) scanner un autre materiel (si le meme materiel est rescanne il est alors mis 
##      a jour (revient en stock et repart)
##   5) ...
## Pour Retourner du materiel en stock il suffit simplement de scanner le dit materiel
##   1) scanner le materiel
##   2) ..... retour en stock
## 
## Le materiel et les membres doivent etre connus et enregistres en base !
##
####################################################################################

import time
import sys
import select
import os
from os import path
from datetime import date, datetime, timedelta
import mysql.connector
from time import sleep
# chemin du dossier lib
sys.path.insert(0, '/lib/')

ficBinMysql='fichiersortie.bin'
varficLogs='logs/scanner_geasm.log'
action='scan'
id_memb='aucun'

def interruptProg(cause):
    global fLogs
    displayOnlcdScreen(cause)
    fLogs.write(datetime.now().strftime("%d-%m-%Y - %H:%M:%S") + " - INFO : Arret du programme\r")
    fLogs.close()
    #print ("Fermeture de l'application")
    exit()

def connexionDB():
    # fonction de connexion a la base de donnee
    print("fonction connexionDB()")
    global fLogs
    global mydb
    global mycursor
    from cryptography.fernet import Fernet
    key = b'nWF2v0zKBnOpWJejRJUobEpScO26PLRlI81H4wFJYOI='
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
        fLogs.write(datetime.now().strftime("%d-%m-%Y - %H:%M:%S") + " - ERROR : MySQL ".format(err) + "\r")
        #print("Erreur de connexion a la base mysql du GEASM: {}".format(err))
        interruptProg("bdd")

# traitement retour du materiel
def retour_materiel(id_materiel, id_mvt):
    # fonction retour du materiel
    print("fonction retour_materiel()")
    global fLogs
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
        displayOnlcdScreen("ret")
    except mysql.connector.Error as err:
        fLogs.write(datetime.now().strftime("%d-%m-%Y - %H:%M:%S") + " - ERROR : MySQL ".format(err) + "\r")
        #print("Erreur de connexion a la base mysql du GEASM: {}".format(err))
        interruptProg("bdd")
	#mettre a jour la table materiel (statut = in au lieu de out)
    #mettre a our la table mvt (date retour ...)
    #retour au mode scan initial

def scan_windows():
    # fonction scanner sur os windows
    # fonction de base qui tourne en boucle pour scanner les codes barres
    print("fonction scan_windows()")
    global fLogs
    fLogs.write(datetime.now().strftime("%d-%m-%Y - %H:%M:%S") + " - INFO : OS Windows\r")
    global action
    global id_memb
    global mydb
    global mycursor
    import msvcrt
    try:
        while True:
            if msvcrt.kbhit():
                if action == 'emprunt':
                    print("fonction scan_windows() action = emprunt")
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
                    print(varToSearch)
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
                        else:
                            fLogs.write(datetime.now().strftime("%d-%m-%Y - %H:%M:%S") + " - WARNING : Code barre inconnu = " + str(varToSearch) + "\r")
                    except mysql.connector.Error as err:
                        fLogs.write(datetime.now().strftime("%d-%m-%Y - %H:%M:%S") + " - ERROR : MySQL ".format(err) + "\r")
                        #print("Erreur de connexion a la base mysql du GEASM: {}".format(err))
                        interruptProg("bdd")
                else:
                    # premier scan
					# suppression de caracteres inutils, probleme lies a windows
                    # un code barre 123456 sera lu et affiche comme suit ['23456']
                    # le premier caracetere n'est pas interprete
                    # suppression des crochets et des '
                    # resultat code barre = 23456
                    print("fonction scan_windows() action = scan")
                    key_stroke = list(input(msvcrt.getch().decode('ascii')).split())
                    varToSearch = str(key_stroke).replace('[', '').replace(']','').replace('\'', '')
                    requete_base("SELECT id_membre FROM membres where id_membre = '" + str(varToSearch) + "'", 'membre', varToSearch)
    except KeyboardInterrupt:
        fLogs.write(datetime.now().strftime("%d-%m-%Y - %H:%M:%S") + " - INFO : interruption clavier\r")
        interruptProg("fin")

def scan_linux():
    # fonction scanner sur os linux
    # fonction de base qui tourne en boucle pour scanner les codes barres
    print("fonction scan_linux()")
    global fLogs
    fLogs.write(datetime.now().strftime("%d-%m-%Y - %H:%M:%S") + " - INFO : OS Linux\r")
    global action
    global id_memb
    global mydb
    global mycursor
    stdin_fd = sys.stdin.fileno()
    try:
        while True:
            if action == 'emprunt':
                displayOnlcdScreen("usr")
                print("fonction scan_windows() action = emprunt")
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
                        displayOnlcdScreen("rec")
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
                            displayOnlcdScreen("emp")
                        else:
                            displayOnlcdScreen("nc")
                            fLogs.write(datetime.now().strftime("%d-%m-%Y - %H:%M:%S") + " - WARNING : Code barre inconnu = " + str(varToSearch) + "\r")
                    except mysql.connector.Error as err:
                            fLogs.write(datetime.now().strftime("%d-%m-%Y - %H:%M:%S") + " - ERROR : MySQL ".format(err) + "\r")
                            #print("Erreur de connexion a la base mysql du GEASM: {}".format(err))
                            interruptProg("bdd")
            else:
                displayOnlcdScreen("main")
                print("fonction scan_windows() action = scan")
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
        fLogs.write(datetime.now().strftime("%d-%m-%Y - %H:%M:%S") + " - INFO : interruption clavier\r")
        interruptProg("fin")

def test_db():
    # procedure de verification connectivite a la base mysql
    # au lancement du programme
    global fLogs
    global mydb
    global mycursor
    print("fonction test_db()")
    connexionDB()
    mydb.close()

def check_if_out(id_materiel):
    # procedure de verification si le materiel est OUT
    # si out ==> on le rentre
    global fLogs
    global mydb
    global mycursor
    #print("check_if_out")
	# verification de l'etat du materiel
    print("fonction check_if_out()")
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
        fLogs.write(datetime.now().strftime("%d-%m-%Y - %H:%M:%S") + " - ERROR : MySQL ".format(err) + "\r")
        #print("Erreur de connexion a la base mysql du GEASM: {}".format(err))
        interruptProg("bdd")

def requete_base(req, type, id):
    # procedure generique d'execution de requetes
    global fLogs
    global id_memb
    global action
    global mydb
    global mycursor
    try:    
        if type == 'insert':
            print("fonction requete_base() type = insert")
            connexionDB()
            mycursor.execute(req)
            mycursor.fetchone()
            mydb.commit()
            mycursor.close()
            mydb.close()
        elif type == 'update':
            print("fonction requete_base() type = update")
            connexionDB()
            mycursor.execute(req)
            mycursor.fetchone()
            mydb.commit()
            mycursor.close()
            mydb.close()
        else:
            print("fonction requete_base() type = autre")
            connexionDB()
            mycursor.execute(req)
            myresult = mycursor.fetchall()
            rc = mycursor.rowcount
            mycursor.close()
            mydb.close()
            if rc == 1:
                if type == 'membre':
                    print("fonction requete_base() type = membre")
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
        fLogs.write(datetime.now().strftime("%d-%m-%Y - %H:%M:%S") + " - ERROR : MySQL ".format(err) + "\r")
        #print("Erreur de connexion a la base mysql du GEASM: {}".format(err))
        interruptProg("bdd")

def displayOnlcdScreen(action):
    # procedure affichage sur lcd2004 (20x4)
    # import driver pour le lcd
    try:
        import lcddriver
        global lcd
        lcd = lcddriver.lcd()
        lcd.lcd_clear()
        if action == "main":
            lcd.lcd_display_string(" - G. E. A. S. M. - ", 1)
            lcd.lcd_display_string("Flash ta carte pour", 2)
            lcd.lcd_display_string("emprunter / Flash un", 3)
            lcd.lcd_display_string("materiel a retourner", 4)
        if action == "fin":
            lcd.lcd_display_string(" - G. E. A. S. M. - ", 1)
            lcd.lcd_display_string("--------------------", 2)
            lcd.lcd_display_string("! PROGRAMME ARRETE !", 3)
            lcd.lcd_display_string("--------------------", 4)
        if action == "bdd":
            lcd.lcd_display_string(" - G. E. A. S. M. - ", 1)
            lcd.lcd_display_string("--------------------", 2)
            lcd.lcd_display_string("! PROGRAMME ARRETE !", 3)
            lcd.lcd_display_string("!  ERREUR BDD/SQL  !", 4)
        if action == "fic":
            lcd.lcd_display_string(" - G. E. A. S. M. - ", 1)
            lcd.lcd_display_string("--------------------", 2)
            lcd.lcd_display_string("! PROGRAMME ARRETE !", 3)
            lcd.lcd_display_string("! ERREUR FIC CONF  !", 4)
        if action == "emp":
            lcd.lcd_display_string(" - G. E. A. S. M. - ", 1)
            lcd.lcd_display_string("--------------------", 2)
            lcd.lcd_display_string("Materiel sorti : OK", 3)
            lcd.lcd_display_string("", 4)
            sleep(3)
        if action == "rec":
            lcd.lcd_display_string(" - G. E. A. S. M. - ", 1)
            lcd.lcd_display_string("--------------------", 2)
            lcd.lcd_display_string("Verification code", 3)
            lcd.lcd_display_string("barre ...", 4)
            sleep(2)
        if action == "nc":
            lcd.lcd_display_string(" - G. E. A. S. M. - ", 1)
            lcd.lcd_display_string("--------------------", 2)
            lcd.lcd_display_string("Code barre inconnu !", 3)
            lcd.lcd_display_string("", 4)
            sleep(3)
        if action == "ret":
            lcd.lcd_display_string(" - G. E. A. S. M. - ", 1)
            lcd.lcd_display_string("--------------------", 2)
            lcd.lcd_display_string("Retour au stock : OK", 3)
            lcd.lcd_display_string("Merci !", 4)
            sleep(3)
        if action == "usr":
            lcd.lcd_display_string(" - G. E. A. S. M. - ", 1)
            lcd.lcd_display_string("--------------------", 2)
            lcd.lcd_display_string("Carte membre : OK", 3)
            lcd.lcd_display_string("-> Flash un materiel", 4)
        if action == "out":
            lcd.lcd_display_string(" - G. E. A. S. M. - ", 1)
            lcd.lcd_display_string("--------------------", 2)
            lcd.lcd_display_string("Materiel hors stock", 3)
            lcd.lcd_display_string("MAJ stock ...", 4)
            sleep(3)
    except:
        print("Erreur LCD : verifier logs, msg = %s" % sys.exc_info()[0])
        fLogs.write(datetime.now().strftime("%d-%m-%Y - %H:%M:%S") + " - ERROR : LCD - msg = %s\r" % sys.exc_info()[0])
        fLogs.write(datetime.now().strftime("%d-%m-%Y - %H:%M:%S") + " - ERROR : LCD - Verifier si l'interface i2c est bien detecte / son emplacement 'commande : sudo i2cdetect -y 1' ==> par defaut 0x27\r")
        fLogs.write(datetime.now().strftime("%d-%m-%Y - %H:%M:%S") + " - ERROR : LCD - Ou configuration emplacement i2c dans lcddriver.py ligne 5\r")
        fLogs.write(datetime.now().strftime("%d-%m-%Y - %H:%M:%S") + " - ERROR : LCD - Ou apt-get install python-smbus i2c-tools\r")

def main():
    global fLogs
    # Main - Debut du programme
    # contole presence dossier logs
    isdir = os.path.isdir("logs/")
    if not isdir:
        os.mkdir("logs")
    if not path.exists(varficLogs):
        fLogs = open(varficLogs, "w")
    else:
        fLogs = open(varficLogs, "a")
    fLogs.write("#######################################################################\r")
    fLogs.write(datetime.now().strftime("%d-%m-%Y - %H:%M:%S") + " - INFO : Lancement du programme\r")
    # controle presence fichier .bin pour mysql
    if not path.exists(ficBinMysql):
        fLogs.write(datetime.now().strftime("%d-%m-%Y - %H:%M:%S") + " - ERROR : fichier " + ficBinMysql + " manquant\r")
        #print("Erreur fichier " + ficBinMysql + " manquant !")
        interruptProg("fic")
    # test de connexion a la base
    test_db()
    # controle OS
    # Si plateforme windows
    if sys.platform.startswith('win'):
        scan_windows()
    else:
        displayOnlcdScreen("main")
        scan_linux()

# Debut appel de main
main()