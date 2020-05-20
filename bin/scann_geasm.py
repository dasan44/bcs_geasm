import time
import sys
import select
import os
from os import path
from datetime import date, datetime, timedelta
import mysql.connector

# un membre scan sa carte puis scan tout le materiel qu'il emprunte
# une fois termine il faut re scanner sa carte / ou scanner une carte FIN

# pour rapporter le materiel il faut scanner le materiel, pas besoin de scanner sa carte

# Fin du programme


# SI SCAN MATERIEL UNIQUEMENT ET QUE LE MATERIEL EST SORTI => UPDATE MATERIEL pour PASSER A IN AU LIEU DE OUT
	# reste à faire : mettre à jour la table MOUVEMENTS
	
# RESTE A FAIRE LA PARTIE EMPRUNT DE MATERIEL

ficBinMysql='mysql.bin'
connection_ok='false'
action='scan'
id_memb='aucun'

def interruptProg():
    print ("Fermeture de l'application")
    exit()


# traitement emprunt du materiel
def scan_materiel(id_emprunteur):
    print("scan du materiel")
    #scanner le materiel a emprunter
    #modification table materiel et table mouvements
    #retour au mode scan initial
    import msvcrt
    if msvcrt.kbhit():
        key_stroke = list(input(msvcrt.getch().decode('ascii')).split())
        # suppression elements
        varToSearch = str(key_stroke).replace('[', '').replace(']','').replace('\'', '')
        #print(varToSearch)
        #requete_base("SELECT id_membre FROM membres where id_membre = '" + varToSearch + "'", 'membre', varToSearch)
        #print(varToSearch)
        print("fin scan materiel")


# traitement retour du materiel
def retour_materiel(id_materiel, id_mvt):
    print("retour_du_materiel")
    #print("UPDATE materiels SET statut = 'in' WHERE id_materiel = '%s'" % id_materiel)
    from cryptography.fernet import Fernet
    key = b'BNDbiQnAZArOCFqQQjvqoq5CcgJOUmYe6S558RDb300='
    cipher_suite = Fernet(key)
    with open(ficBinMysql, 'rb') as file_object:
        for line in file_object:
            encryptedpwd = line
    uncipher_text = (cipher_suite.decrypt(encryptedpwd))
    try:
        mydb = mysql.connector.connect(
         host='192.168.2.76',
         user='geasmpy',
         passwd=bytes(uncipher_text).decode("utf-8"),
         database='geasm',
        auth_plugin='mysql_native_password')
        mycursor = mydb.cursor()
        mycursor.execute("UPDATE materiels SET statut = 'in', id_mvt = '' WHERE id_materiel = '" + str(id_materiel) + "'")
        mycursor.fetchone()
        mydb.commit()
		# on verifie que la requete select n'affiche rien
        mycursor.execute("SELECT id_materiel FROM materiels where id_materiel = '" + str(id_materiel) + "' and statut = 'out'")
        myresult = mycursor.fetchall()
        rc = mycursor.rowcount
		#print("nombre de ligne: "%rc)
        if rc == 1:
            print("ERREUR UPDATE MATERIEL !!!")
        else:
            print("UPDATE OK")
        dateretourcalc = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        mycursor.execute("UPDATE mvts_materiels SET date_retour = '" + str(dateretourcalc) + "' WHERE id_mvt = '" + str(id_mvt) + "'")
        mycursor.fetchone()
        mydb.commit()
        mycursor.execute("SELECT date_retour FROM mvts_materiels where id_mvt = '" + id_mvt + "'")
        myresult = mycursor.fetchall()
        rc = mycursor.rowcount
        mycursor.close()
        mydb.close()
        if rc == 1:
            print("UPDATE OK")
        else:
            print("ERREUR UPDATE MVT!!!")
    except mysql.connector.Error as err:
        print("Erreur de connexion a la base mysql du GEASM: {}".format(err))
        interruptProg()
	#mettre a jour la table materiel (statut = in au lieu de out)
    #mettre a our la table mvt (date retour ...)
    #retour au mode scan initial

def scan_windows():
    global action
    global id_memb
    print("scan_windows")
    import msvcrt
    try:
        while True:
            if msvcrt.kbhit():
                print("ACTION : " + action)
                print("ID MEMBRE : " + id_memb)
                if action == 'emprunt':
                    action = 'scan'
                    key_stroke = list(input(msvcrt.getch().decode('ascii')).split())
                    print("SCAN POUR EMPRUNTER")
					# suppression elements
                    varToSearch = str(key_stroke).replace('[', '').replace(']','').replace('\'', '')
                    # print(varToSearch)
					# inserer une ligne dans la table mvts_materiel
                    print("emprunt du materiel en cours ...")
                    dateretourcalc = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    from cryptography.fernet import Fernet
                    key = b'BNDbiQnAZArOCFqQQjvqoq5CcgJOUmYe6S558RDb300='
                    cipher_suite = Fernet(key)
                    with open(ficBinMysql, 'rb') as file_object:
                        for line in file_object:
                            encryptedpwd = line
                            uncipher_text = (cipher_suite.decrypt(encryptedpwd))
                    try:
                        mydb = mysql.connector.connect(
                         host='192.168.2.76',
                         user='geasmpy',
                         passwd=bytes(uncipher_text).decode("utf-8"),
                         database='geasm',
                         auth_plugin='mysql_native_password')
                        mycursor = mydb.cursor()
                        mycursor.execute("SELECT id_mvt FROM mvts_materiels ORDER BY id_mvt DESC LIMIT 1")
                        myresult = mycursor.fetchall()
                        rc = mycursor.rowcount
						mycursor.close()
						mydb.close()
                        for row in myresult:
                            # incrementation pour table mouvement
                            id_mvt_calc = int(row[0])+1
                        requete_base("INSERT INTO mvts_materiels (id_mvt,id_materiel,id_membre,date_emprunt) VALUES ('%s','%s','%s','%s')" % (id_mvt_calc,varToSearch,id_memb,dateretourcalc), 'insert', id_mvt_calc)
					    # mise a jour table materiel
                        requete_base("UPDATE materiels SET statut = 'out', id_mvt = '%s' WHERE id_materiel = '%s'" % (id_mvt_calc,varToSearch), 'update', varToSearch)

                    except mysql.connector.Error as err:
                        print("Erreur de connexion a la base mysql du GEASM: {}".format(err))
                        interruptProg()
                else:
                    key_stroke = list(input(msvcrt.getch().decode('ascii')).split())
                    print("SCAN NORMAL")
					# suppression elements
                    varToSearch = str(key_stroke).replace('[', '').replace(']','').replace('\'', '')
                    #print(varToSearch)
                    requete_base("SELECT id_membre FROM membres where id_membre = '" + str(varToSearch) + "'", 'membre', varToSearch)
    except KeyboardInterrupt:
        interruptProg()

def scan_linux():
    global action
    global id_memb
    print("scan_linux")
    stdin_fd = sys.stdin.fileno()
    try:
        while True:
            sys.stdout.write("En attente de lecture d'un code barre: ")
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
                    #print ("Code barre scanne: %s" % line)
					#scan_materiel()
                    requete_base("SELECT id_membre FROM membres where id_membre = '" + str(line) + "'", 'membre', line)
    except KeyboardInterrupt:
        interruptProg()

def connect_db(uncipher_text):
    print("connect_db")
    try:
        mydb = mysql.connector.connect(
         host='192.168.2.76',
         user='geasmpy',
         passwd=bytes(uncipher_text).decode("utf-8"),
         database='geasm',
	     auth_plugin='mysql_native_password')
        #mycursor = mydb.cursor()
        #mycursor.execute("SELECT * FROM membres")
        #myresult = mycursor.fetchall()
        #for x in myresult:
        #    print(x)
        #mycursor.close()
        mydb.close()
    except mysql.connector.Error as err:
        print("Erreur de connexion a la base mysql du GEASM: {}".format(err))
        interruptProg()

def check_if_out(id_materiel):
    print("check_if_out")
	# verification de l'etat du materiel
    from cryptography.fernet import Fernet
    key = b'BNDbiQnAZArOCFqQQjvqoq5CcgJOUmYe6S558RDb300='
    cipher_suite = Fernet(key)
    with open(ficBinMysql, 'rb') as file_object:
        for line in file_object:
            encryptedpwd = line
    uncipher_text = (cipher_suite.decrypt(encryptedpwd))
    try:
        mydb = mysql.connector.connect(
         host='192.168.2.76',
         user='geasmpy',
         passwd=bytes(uncipher_text).decode("utf-8"),
         database='geasm',
        auth_plugin='mysql_native_password')
        mycursor = mydb.cursor()
        mycursor.execute("SELECT id_mvt FROM materiels where id_materiel = '" + str(id_materiel) + "' and statut = 'out'")
        myresult = mycursor.fetchall()
        rc = mycursor.rowcount
        mycursor.close()
        mydb.close()
		#print("nombre de ligne: "%rc)
        if rc == 1:
            print("materiel a retourner !")
            for row in myresult:
                #print("id_mvt :", row[0])
                id_mvt = row[0]
            # Materiel identifie comme sorti donc on le rentre (modification de table mvt et materiel)
            retour_materiel(id_materiel, id_mvt)
    except mysql.connector.Error as err:
        print("Erreur de connexion a la base mysql du GEASM: {}".format(err))
        interruptProg()

def requete_base(req, type, id):
    global id_memb
    global action
    #print("requete_base")
    #print(req)
    #print(type)
    #print(id)
    # fonction de requetage en base
    from cryptography.fernet import Fernet
    key = b'BNDbiQnAZArOCFqQQjvqoq5CcgJOUmYe6S558RDb300='
    cipher_suite = Fernet(key)
    with open(ficBinMysql, 'rb') as file_object:
        for line in file_object:
            encryptedpwd = line
    uncipher_text = (cipher_suite.decrypt(encryptedpwd))
    try:
        mydb = mysql.connector.connect(
         host='192.168.2.76',
         user='geasmpy',
         passwd=bytes(uncipher_text).decode("utf-8"),
         database='geasm',
        auth_plugin='mysql_native_password')
        mycursor = mydb.cursor()
        if type == 'insert':
            print("TENTATIVE INSERTION")
            print("la requete : " + str(req))
            mycursor.execute(req)
            mycursor.fetchone()
            mydb.commit()
            mycursor.close()
            mydb.close()
        elif type == 'update':
            print("TENTATIVE UPDATE")
            print("requete UPDATE : " + req)
            mydb = mysql.connector.connect(
             host='192.168.2.76',
             user='geasmpy',
             passwd=bytes(uncipher_text).decode("utf-8"),
             database='geasm',
             auth_plugin='mysql_native_password')
            mycursor = mydb.cursor()
            mycursor.execute(req)
            mycursor.fetchone()
            mydb.commit()
            mycursor.close()
            mydb.close()
        else:
            mycursor.execute(req)
		    #"SELECT * FROM materiels where id_materiel = '%s' and statut = 'out'" % varToSearch
            myresult = mycursor.fetchall()
            rc = mycursor.rowcount
            mycursor.close()
            mydb.close()
            #print("nombre de ligne: %s" % rc)
            if rc == 1:
                #print("rc = 1")
                print("le type : " + type)
                if type == 'membre':
                    for row in myresult:
                        id_memb = row[0]
                        action = 'emprunt'
                        print("appel fonction scan materiel, action : " + action + " et id_memb = " + id_memb)
			            # alors on scan le materiel à sortir
                        scan_materiel(id)
                if type == 'materiel':
                    print("appel fonction is_out")
			        # on verifie si il est sorti
                    check_if_out(id)   
                # Materiel identifie comme sorti donc on le rentre (modification de table mvt et materiel)
                #retour_materiel(varToSearch)
            else:
                #print("rc = 0")
                # on verifie si il ne s'agit pas de materiel qui serait sorti et qui va rentrer
                check_if_out(id) 
		#mycursor = mydb.cursor()
        #mycursor.execute("SELECT * FROM membres")
        #myresult = mycursor.fetchall()
        #for x in myresult:
        #    print(x)
        #mycursor.close()
    except mysql.connector.Error as err:
        print("Erreur de connexion a la base mysql du GEASM: {}".format(err))
        interruptProg()

def main():
    print("main")
    # controle presence fichier .bin pour mysql
    if not path.exists(ficBinMysql):
        print("Erreur fichier " + ficBinMysql + " manquant !")
        interruptProg()
    # mysql
    from cryptography.fernet import Fernet
    key = b'BNDbiQnAZArOCFqQQjvqoq5CcgJOUmYe6S558RDb300='
    cipher_suite = Fernet(key)
    with open(ficBinMysql, 'rb') as file_object:
        for line in file_object:
            encryptedpwd = line
    uncipher_text = (cipher_suite.decrypt(encryptedpwd))
    # test de connexion a la base
    connect_db(uncipher_text)
    # controle OS
    # premier scan = membre
    # Si plateforme windows
    if sys.platform.startswith('win'):
        scan_windows()
    else:
        scan_liux()

# Start
main()