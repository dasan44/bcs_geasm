# bcs_geasm

Scanner de code barre permettant le suivi et la gestion du matériel du club de plongée G.E.A.S.M. : https://www.geasm.org
Emprunter un / des gilet(s) stabilisateur(s), un / des detendeur(s), une / des bouteille(s) / autre materiel appartenant au G.E.A.S.M.

Source montage et librairies LCD 2004 (20x4) : http://hardware-libre.fr/2014/03/raspberry-pi-utiliser-un-lcd-4x20/

Pre-req : La solution complète est destinée à tourner sur Raspbery PI 3
testé sur : Raspbian kernel 4.19 - 2020-02-13-raspbian-buster.img
- MySQL server 
- python 2.7 (minimum), fonctionne sur python 3.7
- apt-get install python-smbus i2c-tools
- pip install mysql-connector-python
- pip install cryptography
- fichier mysql.bin
- Activer l'interface I2C dans Raspbian pour le fonctionnement de l'écran LCD

Lancement du script : ./scanner_geasm ou python scanner_geasm.py

Pour chaque emprunt de materiel il faut scanner sa carte de membre avant !
  1) scanner sa carte de membre
  2) scanner un materiel
  3) scanner sa carte de membre
  4) scanner un autre matériel (si le meme materiel est rescanne il est alors mis 
     a jour (revient en stock et repart)
  5) ...
Pour Retourner du matériel en stock il suffit simplement de scanner le dit matériel
  1) scanner le matériel
  2) ..... retour en stock

Le materiel et les membres doivent etre connus et enregistrés en base, si un code barre n'est pas reconnu (membre ou materiel) il est enregistré dans le fichier de logs
